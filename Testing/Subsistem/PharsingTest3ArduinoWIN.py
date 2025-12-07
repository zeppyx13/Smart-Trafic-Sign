import serial
import time
import json

port = {
    "kota": "COM14",
    "bandara": "COM15",
    "pelabuhan": "COM16"
}
baud_rate = 9600
serial_connections = {}

for name, device in port.items():
    try:
        ser = serial.Serial(device, baud_rate, timeout=1)
        time.sleep(2)
        print(f"Serial terhubung ke {device} untuk {name}")
        serial_connections[name] = ser
    except Exception as e:
        print(f"Gagal membuka port {device} untuk {name}: {e}")
        serial_connections[name] = None

def sendData(target, data):
    if target in serial_connections and serial_connections[target] is not None:
        try:
            json_str = json.dumps(data)
            serial_connections[target].write((json_str + "\n").encode())
            print(f"[SEND] Ke {target}: {json_str}")
        except Exception as e:
            print(f"[ERROR] Gagal mengirim ke {target}: {e}")
    else:
        print(f"Koneksi serial untuk {target} tidak tersedia.")

data = {
    "kota": {
        "nama": "Kota",
        "jumlah": 5,
        "status": "Lancar",
        "eta": 10
    },
    "bandara": {
        "nama": "Bandara",
        "jumlah": 3,
        "status": "Sedang",
        "eta": 15
    },
    "pelabuhan": {
        "nama": "Pelabuhan",
        "jumlah": 7,
        "status": "Padat",
        "eta": 20
    }
}

try:
    while True:
        sendData("kota", data["kota"])
        sendData("bandara", data["bandara"])
        sendData("pelabuhan", data["pelabuhan"])
        time.sleep(5)
except KeyboardInterrupt:
    print("\nDihentikan oleh user.")
except Exception as e:
    print("Terjadi error:", e)
finally:
    for name, ser in serial_connections.items():
        if ser and ser.is_open:
            ser.close()
            print(f"Koneksi serial {name} ditutup.")
    print("Semua koneksi serial ditutup.")