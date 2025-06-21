import serial
import time
import random
import argparse

def generar_trama_peso(tipo):
    if tipo == 'T':
        peso = random.randint(120, 160) * 100  # Tara: 12.000–16.000
    elif tipo == 'B':
        peso = random.randint(450, 580) * 100  # Bruto: 45.000–58.000
    else:
        raise ValueError("Tipo debe ser 'T' para Tara o 'B' para Bruto.")

    peso_str = str(peso) + "00"           # Agrega dos ceros al final
    peso_str = peso_str.zfill(8)          # Asegura 8 dígitos
    cuerpo = f"+{peso_str}BGS"            # Trama con BG + Estado 'S'

    return b'\x02' + cuerpo.encode() + b'\x03'

def main():
    parser = argparse.ArgumentParser(description="Simulador de balanza serial")
    parser.add_argument('--puerto', required=True, help='Puerto COM (ej: COM2)')
    parser.add_argument('--baudrate', type=int, default=1200, help='Velocidad en baudios (por defecto: 1200)')
    parser.add_argument('--tipo', required=True, choices=['T', 'B'], help="Tipo de peso: 'T' para Tara, 'B' para Bruto")

    args = parser.parse_args()

    print(f"🟢 Simulando balanza en {args.puerto} a {args.baudrate} bps, modo {'Tara' if args.tipo == 'T' else 'Bruto'}")

    with serial.Serial(args.puerto, baudrate=args.baudrate) as puerto:
        while True:
            trama = generar_trama_peso(args.tipo)
            print("📤 Enviando trama:", trama)

            for byte in trama:
                puerto.write(bytes([byte]))
                time.sleep(0.01)  # Simula envío realista

            print("⏳ Esperando 5 segundos...\n")
            #time.sleep(5)

if __name__ == "__main__":
    main()
