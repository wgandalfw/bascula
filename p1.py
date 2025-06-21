from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox, QTextEdit, QScrollArea
)
import sys

class FormularioTara(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tara Automática")
        self.setFixedSize(900, 700)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # === Sección principal ===
        grid1 = QGridLayout()

        grid1.addWidget(QLabel("C.Porte"), 0, 0, 0, 10)
        grid1.addWidget(QLineEdit(), 0, 1)
        
        layout.addLayout(grid1)

        # === Botones ===
        botones = QHBoxLayout()
        botones.addWidget(QPushButton("F10 Graba"))
        botones.addWidget(QPushButton("F4-Pesa"))
        botones.addWidget(QPushButton("F9-Leo"))
        botones.addWidget(QPushButton("Anular"))
        botones.addWidget(QPushButton("Movim"))
        botones.addWidget(QPushButton("Balanza"))
        botones.addWidget(QPushButton("Nuevo"))
        layout.addLayout(botones)

        self.setLayout(layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = FormularioTara()
    ventana.show()
    sys.exit(app.exec_())