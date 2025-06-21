import sys
from PyQt5 import QtWidgets, QtCore
from menu_principal import Ui_frmPrincipal
from ventana_bascula import VentanaBascula

class MainApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_frmPrincipal()
        self.ui.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.WindowMinimizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.ui.bascula.clicked.connect(self.abrir_bascula)
        self.ui.salir.clicked.connect(QtWidgets.qApp.quit)

    def abrir_bascula(self):
        self.ventana_bascula = VentanaBascula()
        self.ventana_bascula.setWindowModality(QtCore.Qt.ApplicationModal)
        self.ventana_bascula.setWindowFlags(QtCore.Qt.Dialog |
                                            QtCore.Qt.WindowMinimizeButtonHint |
                                            QtCore.Qt.WindowCloseButtonHint)
        self.ventana_bascula.exec_()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWin = MainApp()
    mainWin.show()
    sys.exit(app.exec_())
