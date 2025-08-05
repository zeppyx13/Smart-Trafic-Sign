import cv2
from ultralytics import YOLO
import serial
import time
import json
import adafruit_ssd1306
import RPi.GPIO as GPIO
from PIL import Image, ImageDraw, ImageFont
from board import SCL, SDA
import busio

GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN)
GPIO.setup(27, GPIO.IN)

i2c = busio.I2C(SCL, SDA)
oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)
oled.fill(0)
oled.show()
image = Image.new("1", (oled.width, oled.height))
draw = ImageDraw.Draw(image)
font = ImageFont.load_default()

#  arduino serial ports
ports = {
    "palang_kota": '/dev/ttyACM0',
    "palang_bandara": '/dev/ttyACM1',
    "palang_pelabuhan": '/dev/ttyACM2'
}
baud_rate = 9600

def oled_display(status_pelabuhan, jumlah_pelabuhan, status_bandara, jumlah_bandara):
    draw.rectangle((0, 0, oled.width, oled.height), outline=0, fill=0)
    draw.text((0, 0), "STATUS JALAN", font=font, fill=255)
    draw.text((0, 16), f"Pelabuhan: {status_pelabuhan} | {jumlah_pelabuhan}", font=font, fill=255)
    draw.text((0, 32), f"Bandara: {status_bandara} | {jumlah_bandara}", font=font, fill=255)
    oled.image(image)
    oled.show()

# cek koneksi serial
serial_connections = {}
for name, port in ports.items():
    try:
        ser = serial.Serial(port, baud_rate, timeout=1)
        time.sleep(2)
        print(f"Serial terhubung ke {port} untuk {name}")
        oled_display("TERHUBUNG", 0, "TERHUBUNG", 0)
        serial_connections[name] = ser
    except Exception as e:
        print(f"Gagal membuka port {port} untuk {name}: {e}")
        oled_display("GAGAL", 0, "GAGAL", 0)
        serial_connections[name] = None

model = YOLO("yolov8n.pt")
id_kendaraan = [2, 3, 5, 7]
nama_kendaraan = {2: 'Car', 3: 'Motor', 5: 'Bus', 7: 'Truck'}


cams = [
    cv2.VideoCapture(0),  # Webcam Bandara
    cv2.VideoCapture(2),  # Webcam Pelabuhan
]

def status_lalu_lintas(jumlah):
    if jumlah >= 9:
        return "macet", "55 menit"
    elif jumlah >= 6:
        return "padat", "30 menit"
    elif jumlah >= 3:
        return "sedang", "15 menit"
    else:
        return "lancar", "5 menit"

def proses_frame(frame, label_arah):
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
    teks = f"{label_arah}: {status} ({jumlah})"
    cv2.putText(frame, teks, (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                0.7, (255, 0, 0), 2)
    return frame, status, eta, jumlah

try:
    waktu_kirim = time.time()
    while True:
        # kamera Bandara
        ret0, frame0 = cams[0].read()
        if ret0:
            frame0 = cv2.resize(frame0, (640, 480))
            frame0, status_bandara, eta_bandara, jumlah_bandara = proses_frame(frame0, "Bandara")
            cv2.imshow("Ruas Bandara", frame0)
        else:
            status_bandara, eta_bandara, jumlah_bandara = "unknown", "0 menit", 0

        # kamera Pelabuhan
        ret1, frame1 = cams[1].read()
        if ret1:
            frame1 = cv2.resize(frame1, (640, 480))
            frame1, status_pelabuhan, eta_pelabuhan, jumlah_pelabuhan = proses_frame(frame1, "Pelabuhan")
            cv2.imshow("Ruas Pelabuhan", frame1)
        else:
            status_pelabuhan, eta_pelabuhan, jumlah_pelabuhan = "unknown", "0 menit", 0
        oled_display(status_pelabuhan, jumlah_pelabuhan, status_bandara, jumlah_bandara)

        #  json data untuk dikirim ke Arduino
        data_palangkota = {
            "bandara": {"arah": "lurus", "jarak": "5km", "status": status_bandara, "eta": eta_bandara},
            "pelabuhan": {"arah": "kanan", "jarak": "7km", "status": status_pelabuhan, "eta": eta_pelabuhan}
        }
        data_palangbandara = {
            "pelabuhan": {"arah": "kiri", "jarak": "16km", "status": status_pelabuhan, "eta": eta_pelabuhan}
        }
        data_palangpelabuhan = {
            "bandara": {"arah": "kanan", "jarak": "7km", "status": status_bandara, "eta": eta_bandara}
        }

        if time.time() - waktu_kirim > 5:
            for name, ser in serial_connections.items():
                if ser and ser.is_open:
                    try:
                        if name == "palang_kota":
                            json_data = json.dumps(data_palangkota, ensure_ascii=False) + '\n'
                        elif name == "palang_bandara":
                            json_data = json.dumps(data_palangbandara, ensure_ascii=False) + '\n'
                        elif name == "palang_pelabuhan":
                            json_data = json.dumps(data_palangpelabuhan, ensure_ascii=False) + '\n'
                        else:
                            continue
                        ser.write(json_data.encode())
                        print(f"[Terkirim ke {name}]: {json_data.strip()}")
                        while ser.in_waiting > 0:
                            response = ser.readline().decode('utf-8', errors='replace').strip()
                            if response:
                                print(f"[Respon Arduino {name}]: {response}")
                    except Exception as e:
                        print(f"[Gagal kirim ke {name}]: {e}")
            waktu_kirim = time.time()

        if cv2.waitKey(1) & 0xFF == 27:
            break

except KeyboardInterrupt:
    print("Berhenti manual.")

finally:
    for cam in cams:
        cam.release()
    cv2.destroyAllWindows()
    for ser in serial_connections.values():
        if ser and ser.is_open:
            ser.close()
    print("Koneksi serial ditutup.")
