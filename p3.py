import sys
import cv2
from pyzbar.pyzbar import decode
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QMessageBox

class QRScanner(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TOPO C100 - Escaner QR")
        # Label para mostrar el video adaptado a 250x250
        self.video_label = QLabel()
        self.video_label.setFixedSize(500, 500)
        # Label para mostrar el valor del QR
        self.qr_label = QLabel("Esperando QR...")
        self.qr_label.setAlignment(Qt.AlignCenter)
        # Layout vertical
        layout = QVBoxLayout()
        layout.addWidget(self.video_label)
        layout.addWidget(self.qr_label)
        self.setLayout(layout)

        # URL del stream RTSP
        self.url = 'rtsp://camaragarage:Iara2025_@192.168.100.220:554/stream1'
        # Inicializar captura de video
        self.cap = cv2.VideoCapture(self.url, cv2.CAP_FFMPEG)
        if not self.cap.isOpened():
            QMessageBox.critical(self, "Error", "No se pudo abrir el stream RTSP.")
            sys.exit(1)

        # Timer para actualizar frames
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # Aproximadamente 30 ms entre frames

    def update_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            print("Error al leer el stream.")
            return

        # Decodificar códigos QR
        qr_codes = decode(frame)
        for qr in qr_codes:
            data = qr.data.decode('utf-8')
            # Actualizar texto del label
            self.qr_label.setText(data)
            # Dibujar rectángulo alrededor del QR
            pts = qr.polygon
            if len(pts) > 4:
                pts = pts[:4]
            for i in range(len(pts)):
                pt1 = pts[i]
                pt2 = pts[(i + 1) % len(pts)]
                cv2.line(frame, (pt1.x, pt1.y), (pt2.x, pt2.y), (0, 255, 0), 2)
            # Mostrar texto encima del QR
            cv2.putText(frame, data, (qr.rect.left, qr.rect.top - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

        # Convertir BGR (OpenCV) a RGB (Qt)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w
        qimg = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimg)
        # Escalar pixmap para encajar en 250x250
        pixmap = pixmap.scaled(self.video_label.width(), self.video_label.height(), Qt.KeepAspectRatio)
        self.video_label.setPixmap(pixmap)

    def closeEvent(self, event):
        # Liberar recursos al cerrar
        self.timer.stop()
        self.cap.release()
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QRScanner()
    window.show()
    sys.exit(app.exec_())
