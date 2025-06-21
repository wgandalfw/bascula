import sys
import serial
import random
import time
from PyQt5 import QtWidgets, QtCore


def generar_trama_peso(tipo):
    """
    Genera una trama de peso para 'T' (Tara) o 'B' (Bruto).
    Formato: STX + '+' + 8 dígitos de peso + 'BGS' + ETX
    """
    if tipo == 'T':
        peso = random.randint(120, 160) * 100  # 12.000–16.000
    else:
        peso = random.randint(450, 580) * 100  # 45.000–58.000

    peso_str = str(peso) + "00"
    peso_str = peso_str.zfill(8)
    cuerpo = f"+{peso_str}BGS"
    return b'\x02' + cuerpo.encode() + b'\x03'


class SenderThread(QtCore.QThread):
    log = QtCore.pyqtSignal(str)

    def __init__(self, puerto, baud, tipo, parent=None):
        super().__init__(parent)
        self.puerto = puerto
        self.baud = baud
        self.tipo = tipo
        self._running = True

    def run(self):
        try:
            ser = serial.Serial(self.puerto, baudrate=self.baud, timeout=1)
        except serial.SerialException as e:
            self.log.emit(f"❌ Error al abrir {self.puerto}: {e}")
            return

        self.log.emit(f"🟢 Iniciando envío continuo de '{self.tipo}' en {self.puerto}@{self.baud}")
        while self._running:
            trama = generar_trama_peso(self.tipo)
            ser.write(trama)
            ser.flush()
            self.log.emit(f"✅ Enviado {self.tipo}: {trama}")
            time.sleep(5)  # Intervalo de 5 segundos
        ser.close()
        self.log.emit("🛑 Envío detenido")

    def stop(self):
        self._running = False


class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.thread = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Simulador Balanza Qt5")
        layout = QtWidgets.QVBoxLayout()

        form_layout = QtWidgets.QFormLayout()
        self.portEdit = QtWidgets.QLineEdit("COM2")
        self.baudEdit = QtWidgets.QLineEdit("1200")
        form_layout.addRow("Puerto:", self.portEdit)
        form_layout.addRow("Baudrate:", self.baudEdit)
        layout.addLayout(form_layout)

        btn_layout = QtWidgets.QHBoxLayout()
        self.btnTara = QtWidgets.QPushButton("Tara")
        self.btnBruto = QtWidgets.QPushButton("Bruto")
        btn_layout.addWidget(self.btnTara)
        btn_layout.addWidget(self.btnBruto)
        layout.addLayout(btn_layout)

        self.output = QtWidgets.QTextEdit()
        self.output.setReadOnly(True)
        layout.addWidget(self.output)

        self.setLayout(layout)

        self.btnTara.clicked.connect(lambda: self.start_sending('T'))
        self.btnBruto.clicked.connect(lambda: self.start_sending('B'))

    def start_sending(self, tipo):
        # Detener hilo anterior si existe
        if self.thread is not None:
            self.thread.stop()
            self.thread.wait()

        puerto = self.portEdit.text().strip()
        try:
            baud = int(self.baudEdit.text())
        except ValueError:
            self.output.append("🔴 Baudrate inválido")
            return

        # Iniciar nuevo hilo de envío continuo
        self.thread = SenderThread(puerto, baud, tipo)
        self.thread.log.connect(self.output.append)
        self.thread.start()

    def closeEvent(self, event):
        # Asegurar que el hilo se detenga al cerrar la ventana
        if self.thread is not None:
            self.thread.stop()
            self.thread.wait()
        event.accept()


def main():
    app = QtWidgets.QApplication(sys.argv)
    win = MainWindow()
    win.resize(350, 300)
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
