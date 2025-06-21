from PyQt5.QtCore import QThread, pyqtSignal

class HiloCapturaPeso(QThread):
    peso_capturado = pyqtSignal(float)

    def __init__(self, capturador):
        super().__init__()
        self.capturador = capturador

    def run(self):
        peso = self.capturador.capturar()
        try:
            self.peso_capturado.emit(float(peso))
        except:
            self.peso_capturado.emit(0.0)
