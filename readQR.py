import cv2
from pyzbar.pyzbar import decode

# URL del stream RTSP de tu cámara
url = 'rtsp://camaragarage:Iara2025_@192.168.100.220:554/stream1'

cap = cv2.VideoCapture(url, cv2.CAP_FFMPEG)

if not cap.isOpened():
    print("No se pudo abrir el stream RTSP.")
    exit()

print("Escaneando QR en tiempo real. Presioná 'q' para salir.")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error al leer el stream.")
        break

    # Decodificar cualquier QR visible en el frame
    qr_codes = decode(frame)

    for qr in qr_codes:
        data = qr.data.decode('utf-8')
        print(f"[QR Detectado] → {data}")

        # Dibujar un rectángulo alrededor del QR
        pts = qr.polygon
        if len(pts) > 4: pts = pts[:4]
        pts = [(pt.x, pt.y) for pt in pts]
        for i in range(len(pts)):
            cv2.line(frame, pts[i], pts[(i+1) % len(pts)], (0, 255, 0), 2)

        # Mostrar el texto encima
        cv2.putText(frame, data, (qr.rect.left, qr.rect.top - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

    # Mostrar la imagen con posibles códigos QR marcados
    cv2.imshow("TOPO C100 - Escaner QR", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
