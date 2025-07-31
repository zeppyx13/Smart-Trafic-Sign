import cv2
from ultralytics import YOLO
import serial
import time

arduino_port = 'COM7'  # Arduino Port
# (Raspi: '/dev/ttyACM0' atau '/dev/ttyUSB0')
baud_rate = 9600

try:
    ser = serial.Serial(arduino_port, baud_rate, timeout=1)
    time.sleep(2)
    print("Serial terhubung ke", arduino_port)
except Exception as e:
    print("Gagal membuka port serial:", e)
    ser = None

model = YOLO("yolov8n.pt")

cams = [
    cv2.VideoCapture(0),
    cv2.VideoCapture(2),
]

# === Konfigurasi Deteksi ===
id_kendaraan = [2, 3, 5, 7]
nama_kendaraan = {2: 'Car', 3: 'Motor', 5: 'Bus', 7: 'Truck'}

def status_lalu_lintas(jumlah):
    if jumlah >= 9:
        return "Macet", 20
    elif jumlah >= 6:
        return "Padat", 15
    elif jumlah >= 3:
        return "Sedang", 10
    else:
        return "Lancar", 5

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

    status, eta = status_lalu_lintas(jumlah)
    teks = f"Arah {cam_index+1}: {status} ({jumlah} kendaraan)"
    cv2.putText(frame, teks, (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                0.7, (255, 0, 0), 2)

    return frame, status, eta, jumlah

try:
    waktu_kirim = time.time()
    while True:
        status_list = []
        for i, cam in enumerate(cams):
            ret, frame = cam.read()
            if not ret:
                print(f"Webcam {i} tidak terdeteksi.")
                continue

            frame = cv2.resize(frame, (640, 480))
            frame, status, eta, jumlah = proses_frame(frame, i)
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

                    # Terima respons jika ada
                    while ser.in_waiting > 0:
                        response = ser.readline().decode('utf-8', errors='replace').strip()
                        if response:
                            print("Dari Arduino:", response)

                except Exception as e:
                    print("Gagal kirim:", e)

            waktu_kirim = time.time()

        if cv2.waitKey(1) & 0xFF == 27:
            break

except KeyboardInterrupt:
    print("Quitting...")

finally:
    for cam in cams:
        cam.release()
    cv2.destroyAllWindows()
    if ser and ser.is_open:
        ser.close()
    print("Selesai dan koneksi ditutup.")
