import cv2
from ultralytics import YOLO
import serial
import time

Port = 'COM11'
# Port = '/dev/ttyACM0'
baud_rate = 9600

try:
    ser = serial.Serial(Port, baud_rate, timeout=1)
    time.sleep(2)
    print("Serial terhubung ke", Port)
except Exception as e:
    print("Gagal membuka port serial:", e)
    ser = None

model = YOLO("../yolov8n.pt")

# === Webcam Setup ===
cams = [
    cv2.VideoCapture(0),
    cv2.VideoCapture(2),
]


id_kendaraan = [2, 3, 5, 7]
nama_kendaraan = {2: 'Car', 3: 'Motor', 5: 'Bus', 7: 'Truck'}

# === ETA ===
def hitung_eta_dinamis(jumlah):
    kecepatan_normal = 30  # km/jam
    jarak_km = 1.5

    # Semakin padat → kecepatan berkurang kecepatannya
    if jumlah >= 10:
        kecepatan = 5
        status = "Macet"
    elif jumlah >= 7:
        kecepatan = 10
        status = "Padat"
    elif jumlah >= 3:
        kecepatan = 20
        status = "Sedang"
    else:
        kecepatan = kecepatan_normal
        status = "Lancar"

    eta_menit = round((jarak_km / kecepatan) * 60)
    return status, eta_menit

def proses_frame(frame, cam_index):
    hasil = model(frame, verbose=False)[0]
    jumlah = 0

    for box in hasil.boxes:
        cls_id = int(box.cls)
        if cls_id in id_kendaraan:
            jumlah += 1
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            label = nama_kendaraan.get(cls_id, "Kendaraan")
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, label, (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    status, eta = hitung_eta_dinamis(jumlah)
    teks = f"Arah {cam_index+1}: {status} ({jumlah} kendaraan)"
    cv2.putText(frame, teks, (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                0.7, (255, 0, 0), 2)

    return frame, status, eta

try:
    waktu_kirim = time.time()
    while True:
        status_list = []
        for i, cam in enumerate(cams):
            ret, frame = cam.read()
            if not ret:
                print(f"Webcam {i} tidak terbaca.")
                continue

            frame = cv2.resize(frame, (640, 480))
            frame, status, eta = proses_frame(frame, i)
            status_list.append((i, status, eta))

            cv2.imshow(f"Webcam {i+1}", frame)

        if time.time() - waktu_kirim > 5:
            if len(status_list) == 2 and ser:
                arah_data = [
                    f"⬆|Bandara|2|{status_list[0][1]}|{status_list[0][2]}",
                    f"➡|Pelabuhan|3|{status_list[1][1]}|{status_list[1][2]}"
                ]
                data_kirim = ";".join(arah_data) + "\n"

                try:
                    ser.write(data_kirim.encode())
                    print("Terkirim:", data_kirim.strip())

                    # Cek respons dari Arduino
                    while ser.in_waiting > 0:
                        response = ser.readline().decode('utf-8', errors='replace').strip()
                        if response:
                            print("Dari Arduino:", response)

                except Exception as e:
                    print("Gagal kirim:", e)

            waktu_kirim = time.time()

        if cv2.waitKey(1) & 0xFF == 27:  # ESC untuk keluar
            break

except KeyboardInterrupt:
    print("Quitting,,,,")

finally:
    for cam in cams:
        cam.release()
    cv2.destroyAllWindows()
    if ser and ser.is_open:
        ser.close()
    print("CLOSED.")
