import cv2
from ultralytics import YOLO
import serial
import time
ser = serial.Serial('COM4', 9600, timeout=1)  #port Arduino

model = YOLO("yolov8n.pt")

cap = cv2.VideoCapture(0)  # webcam

def hitung_status(jumlah):
    if jumlah >= 6:
        return "Padat", 15
    elif jumlah >= 3:
        return "Sedang", 10
    else:
        return "Lancar", 5

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            continue
        frame = cv2.resize(frame, (640, 480))
        results = model(frame, verbose=False)[0]
        kendaraan = [r for r in results.boxes.cls if int(r) in [2, 3, 5, 7]]  # class 2=car, 3=motor, 5=bus, 7=truck
        jumlah_kendaraan = len(kendaraan)
        status1, eta1 = hitung_status(jumlah_kendaraan)
        status2, eta2 = hitung_status(jumlah_kendaraan // 2)
        teks_pelang = f"⬆|Bandara|2|{status1}|{eta1};➡|Pelabuhan|3|{status2}|{eta2}\n"
        ser.write(teks_pelang.encode())
        cv2.putText(frame, f"Kendaraan: {jumlah_kendaraan}", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
        cv2.imshow("Deteksi Kendaraan", frame)
        print("Terkirim:", teks_pelang.strip())
        if cv2.waitKey(1) == 27:
            break

except KeyboardInterrupt:
    print("Dihentikan manual.")
finally:
    cap.release()
    cv2.destroyAllWindows()
    ser.close()