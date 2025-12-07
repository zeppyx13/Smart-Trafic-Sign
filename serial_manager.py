import serial
import time
import json

def init_serial(ports, baud_rate):
    serial_connections = {}
    for name, port in ports.items():
        try:
            ser = serial.Serial(port, baud_rate, timeout=1)
            time.sleep(2)
            print(f"[INFO] Serial terhubung ke {port} untuk {name}")
            serial_connections[name] = ser
        except Exception as e:
            print(f"[ERROR] Gagal membuka {port} untuk {name}: {e}")
            serial_connections[name] = None
    return serial_connections


def send_json(serial_connections, name, data):
    ser = serial_connections.get(name)
    if ser and ser.is_open:
        try:
            json_data = json.dumps(data) + '\n'
            ser.write(json_data.encode())
            print(f"[Terkirim ke {name}]: {json_data.strip()}")
        except Exception as e:
            print(f"[ERROR Kirim ke {name}]: {e}")
