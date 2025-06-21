from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow

class MiVentana(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("gt5frm/menu_principal.ui", self)
        uic.loadUi("gt5frm/prueba.ui", self)

app = QApplication([])
ventana = MiVentana()
ventana.show()
app.exec_()
