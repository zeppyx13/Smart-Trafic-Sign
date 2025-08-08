import cv2
from ultralytics import YOLO
import serial
import time
import json

# Port serial Arduino untuk masing-masing palang
ports = {
    "palang_kota": 'COM5',
    "palang_pelabuhan": 'COM6',
    "palang_bandara": 'COM7',
    "trafic_light": 'COM8'
}

baud_rate = 9600
serial_connections = {}
for name, port in ports.items():
    try:
        ser = serial.Serial(port, baud_rate, timeout=1)
        time.sleep(2)
        print(f"[INFO] Serial terhubung ke {port} untuk {name}")
        serial_connections[name] = ser
    except Exception as e:
        print(f"[ERROR] Gagal membuka port {port} untuk {name}: {e}")
        serial_connections[name] = None

model = YOLO("yolov8n.pt")

cams = [
    cv2.VideoCapture(0),
    cv2.VideoCapture(4),
]

id_kendaraan = [2, 3, 5, 7]
nama_kendaraan = {2: 'Car', 3: 'Motor', 5: 'Bus', 7: 'Truck'}

def status_lalu_lintas(jumlah):
    if jumlah >= 9:
        return "macet", "55 menit"
    elif jumlah >= 6:
        return "padat", "30 menit"
    elif jumlah >= 3:
        return "sedang", "15 menit"
    else:
        return "lancar", "5 menit"

def parse_eta(eta):
    if isinstance(eta, (int, float)):
        return eta
    eta = eta.lower().replace("menit", "").replace("m", "").strip()
    try:
        return int(eta)
    except:
        return 1

def trafic_duration(status_bandara, eta_bandara, status_pelabuhan, eta_pelabuhan, total_duration=30):
    status_score = {
        "lancar": 1,
        "sedang": 2,
        "padat": 3,
        "macet": 4
    }
    score_bandara = status_score.get(status_bandara.lower(), 1)
    score_pelabuhan = status_score.get(status_pelabuhan.lower(), 1)
    eta_bandara = parse_eta(eta_bandara)
    eta_pelabuhan = parse_eta(eta_pelabuhan)
    beban_bandara = score_bandara * eta_bandara
    beban_pelabuhan = score_pelabuhan * eta_pelabuhan
    total_beban = beban_bandara + beban_pelabuhan
    if total_beban == 0:
        return {"bandara": total_duration // 2, "pelabuhan": total_duration // 2}
    durasi_bandara = int((beban_bandara / total_beban) * total_duration)
    durasi_pelabuhan = total_duration - durasi_bandara
    return {"bandara": durasi_bandara, "pelabuhan": durasi_pelabuhan}

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
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    status, eta = status_lalu_lintas(jumlah)
    teks = f"{label_arah}: {status} ({jumlah})"
    cv2.putText(frame, teks, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
    return frame, status, eta

try:
    waktu_kirim = time.time()
    while True:
        ret0, frame0 = cams[0].read()
        if ret0:
            frame0 = cv2.resize(frame0, (640, 480))
            frame0, status_bandara, eta_bandara = proses_frame(frame0, "Bandara")
            cv2.imshow("Ruas Bandara", frame0)
        else:
            status_bandara, eta_bandara = "unknown", "0 menit"

        ret1, frame1 = cams[1].read()
        if ret1:
            frame1 = cv2.resize(frame1, (640, 480))
            frame1, status_pelabuhan, eta_pelabuhan = proses_frame(frame1, "Pelabuhan")
            cv2.imshow("Ruas Pelabuhan", frame1)
        else:
            status_pelabuhan, eta_pelabuhan = "unknown", "0 menit"

        data_palangkota = {
            "bandara": {
                "arah": "lurus",
                "jarak": "5km",
                "status": status_bandara,
                "eta": eta_bandara,
                "alternatif": "via Pelabuhan" if status_bandara in ["padat", "macet"] else ""
            },
            "pelabuhan": {
                "arah": "kanan",
                "jarak": "7km",
                "status": status_pelabuhan,
                "eta": eta_pelabuhan,
                "alternatif": "via Bandara" if status_pelabuhan in ["padat", "macet"] else ""
            }
        }

        data_palangbandara = {
            "pelabuhan": {
                "arah": "kiri",
                "jarak": "16km",
                "status": status_pelabuhan,
                "eta": eta_pelabuhan,
                "alternatif": "via Kota lalu ke Pelabuhan" if status_pelabuhan in ["padat", "macet"] else ""
            }
        }

        data_palangpelabuhan = {
            "bandara": {
                "arah": "kanan",
                "jarak": "7km",
                "status": status_bandara,
                "eta": eta_bandara,
                "alternatif": "via Kota lalu ke Bandara" if status_bandara in ["padat", "macet"] else ""
            }
        }

        duration = trafic_duration(status_bandara, eta_bandara, status_pelabuhan, eta_pelabuhan)
        data_trafic_light = {
            "lampu": {
                "ke_bandara": duration["bandara"],
                "ke_pelabuhan": duration["pelabuhan"]
            }
        }

        if time.time() - waktu_kirim > 3:
            for name, ser in serial_connections.items():
                if ser and ser.is_open:
                    try:
                        if name == "palang_kota":
                            json_data = json.dumps(data_palangkota, ensure_ascii=False) + '\n'
                        elif name == "palang_bandara":
                            json_data = json.dumps(data_palangbandara, ensure_ascii=False) + '\n'
                        elif name == "palang_pelabuhan":
                            json_data = json.dumps(data_palangpelabuhan, ensure_ascii=False) + '\n'
                        elif name == "trafic_light":
                            json_data = json.dumps(data_trafic_light, ensure_ascii=False) + '\n'
                        else:
                            continue
                        ser.write(json_data.encode())
                        print(f"[Terkirim ke {name}]: {json_data.strip()}")

                        while ser.in_waiting > 0:
                            response = ser.readline().decode('utf-8', errors='replace').strip()
                            if response:
                                print(f"[Respon Arduino {name}]: {response}")
                    except Exception as e:
                        print(f"[ERROR Kirim ke {name}]: {e}")
            waktu_kirim = time.time()

        if cv2.waitKey(1) & 0xFF == 27:
            break

except KeyboardInterrupt:
    print("\n[Dihentikan secara manual]")

finally:
    for cam in cams:
        cam.release()
    cv2.destroyAllWindows()
    for ser in serial_connections.values():
        if ser and ser.is_open:
            ser.close()
    print("[Koneksi serial & kamera ditutup]")
