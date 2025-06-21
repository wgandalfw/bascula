import sys
import cv2
from pyzbar.pyzbar import decode
from PyQt5 import QtWidgets, QtCore, QtGui
from bascula import Ui_frmBascula
from serialport import CapturadorPesada
from hilo_captura import HiloCapturaPeso
from models import get_engine, CanePesosBalanza, CaneBalanzaInfo, CaneBalanzaHora, CaneMovimPeso
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

class VentanaBascula(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Ui_frmBascula()
        self.ui.setupUi(self)
        self.ui.vehiculo.installEventFilter(self)

        # Shortcuts y configuración de pesaje
        self.shortcut_guardar = QtWidgets.QShortcut(
            QtGui.QKeySequence(QtCore.Qt.Key_F10),
            self,
            context=QtCore.Qt.WidgetWithChildrenShortcut
        )
        self.shortcut_guardar.activated.connect(self.mostrar_proceso_guardado)

        self.capturador = CapturadorPesada('COM3', 1200)
        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(2000)
        self.timer.timeout.connect(self.lanzar_hilo_captura)
        self.timer.start()
        self.cargar_historico()
        self.cargar_acumulado()

        # Configurar cámara y QR en cam_entrar
        self.url = 'rtsp://camaragarage:Iara2025_@192.168.100.220:554/stream1'
        self.cap = cv2.VideoCapture(self.url, cv2.CAP_FFMPEG)
        if not self.cap.isOpened():
            QtWidgets.QMessageBox.warning(self, "Error", "No se pudo abrir el stream RTSP.")
        else:
            self.timer_qr = QtCore.QTimer(self)
            self.timer_qr.timeout.connect(self.update_cam_entrada)
            self.timer_qr.start(30)

    def update_cam_entrada(self):
        ret, frame = self.cap.read()
        if not ret:
            return

        # Detectar y print QR
        qr_codes = decode(frame)
        for qr in qr_codes:
            data = qr.data.decode('utf-8')
            print(f"[QR Detectado] → {data}")
            # Opcional: dibujar rectángulo
            pts = qr.polygon
            if len(pts) > 4:
                pts = pts[:4]
            for i in range(len(pts)):
                pt1 = pts[i]
                pt2 = pts[(i + 1) % len(pts)]
                cv2.line(frame, (pt1.x, pt1.y), (pt2.x, pt2.y), (0, 255, 0), 2)
            cv2.putText(frame, data, (qr.rect.left, qr.rect.top - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

        # Mostrar frame en label cam_entrar
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        bytes_per_line = ch * w
        qimg = QtGui.QImage(rgb.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        pixmap = QtGui.QPixmap.fromImage(qimg)
        pixmap = pixmap.scaled(self.ui.cam_entrar.width(), self.ui.cam_entrar.height(), QtCore.Qt.KeepAspectRatio)
        self.ui.cam_entrar.setPixmap(pixmap)
        self.ui.cam_salir.setPixmap(pixmap)

    def mostrar_proceso_guardado(self):
        QtWidgets.QMessageBox.information(self, "Proceso", "Proceso Guardado")

    def lanzar_hilo_captura(self):
        self.hilo = HiloCapturaPeso(self.capturador)
        self.hilo.peso_capturado.connect(self.ui.bascula.display)
        self.hilo.start()

    def eventFilter(self, obj, event):
        if obj == self.ui.vehiculo and event.type() == QtCore.QEvent.KeyPress:
            if event.key() == QtCore.Qt.Key_F9:
                QtWidgets.QMessageBox.information(self, "Búsqueda", "Busqueda de Viajes")
                return True
            if event.key() in (QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter, QtCore.Qt.Key_Tab):
                engine = get_engine("fctrinidad", "pen", "localhost", 1521, "orcl")
                session = sessionmaker(bind=engine)()
                fila = session.query(CanePesosBalanza).filter_by(vehiculo=self.ui.vehiculo.text()).first()
                if not fila:
                    QtWidgets.QMessageBox.warning(self, "Error", "Vehículo no encontrado.")
                    session.close()
                    return True
                renglon = session.query(CaneBalanzaInfo).filter_by(cporte=fila.cporte, zafra=fila.zafra).first()
                peso = session.query(CaneMovimPeso).filter_by(cporte=fila.cporte, zafra=fila.zafra).first()
                session.close()
                self.ui.cporte.setText(str(fila.cporte))
                self.ui.fletero.setText(renglon.fletero)
                self.ui.desc_fletero.setText("Fletero de prueba")
                self.ui.canero.setText(renglon.canero)
                self.ui.contrato.setText(renglon.contrato)
                self.ui.cosechador.setText(renglon.cosechador)
                self.ui.tcosecha.setText(renglon.tipo_cosecha)
                self.ui.desc_tcosecha.setText(renglon.desc_tipocosecha)
                self.ui.tcana.setText(renglon.tipo_cana)
                self.ui.desc_tcana.setText(renglon.desc_tipocana)
                self.ui.cana_bruta.setText(str(renglon.cana_bruta))
                self.ui.trashpor.setText(str(renglon.trashpor))
                self.ui.trashkgs.setText(str(renglon.trash))
                self.ui.neto_sucio.setText(str(renglon.bruto))
                self.ui.tara.setText(str(renglon.tara))
                return True
        return super().eventFilter(obj, event)

    def cargar_historico(self):
        engine = get_engine("fctrinidad", "pen", "localhost", 1521, "orcl")
        Session = sessionmaker(bind=engine)
        session = Session()
        registros = session.query(CaneBalanzaHora).limit(3).all()
        session.close()
        tabla = self.ui.historico
        tabla.setRowCount(0)
        tabla.clearContents()
        tabla.setColumnCount(4)
        tabla.setHorizontalHeaderLabels(["Hora", "Bruto", "K.Trash", "Neto"])
        tabla.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        for fila, registro in enumerate(registros):
            tabla.insertRow(fila)
            tabla.setRowHeight(fila, 24)
            items = [str(registro.hora), f"{registro.bruto:,.0f}".replace(",", "."), f"{registro.ktrash:,.0f}".replace(",", "."), f"{registro.neto:,.0f}".replace(",", ".")]
            for col, val in enumerate(items):
                item = QtWidgets.QTableWidgetItem(val)
                if col > 0:
                    item.setTextAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
                tabla.setItem(fila, col, item)

    def cargar_acumulado(self):
        engine = get_engine("fctrinidad", "pen", "localhost", 1521, "orcl")
        Session = sessionmaker(bind=engine)
        session = Session()
        fila = engine.connect().execute(text(
            "select sum(cana_neta) total_bruto, sum(neto) total_neto, sum(trash) total_trash, count(*) total_viajes from cane_movim_w where fecha_analisis = trunc(sysdate)"
        )).first()
        def fmt(v): return "0" if v is None else f"{v:,.0f}".replace(",", ".")
        self.ui.acum_bruto.setText(fmt(fila.total_bruto))
        self.ui.acum_neto.setText(fmt(fila.total_neto))
        self.ui.acum_trash.setText(fmt(fila.total_trash))
        self.ui.acum_viajes.setText(fmt(fila.total_viajes))

    def closeEvent(self, event):
        # Detener timer de captura de pesaje
        if self.timer.isActive():
            self.timer.stop()
        # Detener hilo si corre
        if hasattr(self, 'hilo') and self.hilo.isRunning():
            self.hilo.wait()
        # Cerrar puerto serial
        self.capturador.cerrar()
        # Liberar cámara
        if hasattr(self, 'cap'):
            self.cap.release()
        event.accept()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    win = VentanaBascula()
    win.show()
    sys.exit(app.exec_())
