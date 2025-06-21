import serial
import os
import sys
import json
from datetime import datetime

TRAMAS_NECESARIAS = 1


class CapturadorPesada:
    def __init__(self, puerto: str, baudrate: int):
        self.puerto = puerto
        self.baudrate = baudrate
        self.ser = None
        #self.abrir_puerto()

    def abrir_puerto(self):
        if self.ser is None or not self.ser.is_open:
            self.ser = serial.Serial(
                port=self.puerto,
                baudrate=self.baudrate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=1
            )
    
    def cerrar(self):
        if self.ser and self.ser.is_open:
            self.ser.close()
            print("[INFO] Puerto cerrado correctamente.")
            self.ser = None
        
    @staticmethod
    def obtener_ruta_config(nombre_archivo="config.json"):
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_path, nombre_archivo)

    @staticmethod
    def cargar_config():
        ruta_config = CapturadorPesada.obtener_ruta_config()
        if not os.path.exists(ruta_config):
            raise FileNotFoundError(f"No se encontró {ruta_config}")
        with open(ruta_config, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def limpiar_trama(buffer: bytes):
        try:
            texto = buffer.decode('utf-8', errors='ignore').strip()
            if not texto.startswith('+') or not texto[-1] in ('S', 's'):
                return None
            if not texto.endswith(('GS', 'NS')):
                return None
            peso_str = texto[1:-5]
            peso_num = int(peso_str)
            return f"{peso_num}"
        except Exception:
            return None

    def capturar(self):
        """
        Abre el puerto, lee hasta encontrar una trama válida y devuelve el peso,
        luego cierra el puerto siempre (incluso ante errores).
        """
        try:
            # 1) Abrir puerto una sola vez
            self.abrir_puerto()

            # 2) Leer hasta encontrar una trama válida
            while True:
                byte = self.ser.read(1)
                if not byte or byte[0] != 0x02:
                    continue

                trama = self.ser.read(13)
                if len(trama) != 13 or trama[-1] != 0x03:
                    continue

                payload = trama[:12]
                peso = self.limpiar_trama(payload)
                if peso is not None:
                    print(f"[INFO] Peso capturado: {peso}")
                    return peso  # sale del método, pasa al finally

        except Exception as e:
            print(f"[ERROR] {e}")
            return "-1"

        finally:
            # 3) Cerrar siempre el puerto al terminar
            if self.ser and self.ser.is_open:
                self.ser.close()
                print("[INFO] Puerto cerrado correctamente.")
                self.ser = None

