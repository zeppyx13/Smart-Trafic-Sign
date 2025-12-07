import cv2
import time

from config import ports, baud_rate
from serial_manager import init_serial, send_json
from camera import proses_frame
from traffic_logic import hitung_eta, trafic_duration


def main():
    cams = [
        cv2.VideoCapture(0),
        cv2.VideoCapture(3),
    ]

    serial_con = init_serial(ports, baud_rate)

    waktu_kirim = time.time()

    try:
        while True:
            # Kamera 0
            ret0, frame0 = cams[0].read()
            status_bandara = "unknown"
            if ret0:
                frame0 = cv2.resize(frame0, (640, 480))
                frame0, status_bandara = proses_frame(frame0, "Bandara")
                cv2.imshow("Ruas Bandara", frame0)

            # Kamera 3
            ret1, frame1 = cams[1].read()
            status_pelabuhan = "unknown"
            if ret1:
                frame1 = cv2.resize(frame1, (640, 480))
                frame1, status_pelabuhan = proses_frame(frame1, "Pelabuhan")
                cv2.imshow("Ruas Pelabuhan", frame1)

            # ETA
            eta_bandara = hitung_eta(5, status_bandara)
            eta_pelabuhan = hitung_eta(7, status_pelabuhan)

            # Paket data
            data_palangkota = {
                "bandara": {"arah": "kiri", "jarak": "5km",
                            "status": status_bandara, "eta": eta_bandara},
                "pelabuhan": {"arah": "lurus", "jarak": "7km",
                              "status": status_pelabuhan, "eta": eta_pelabuhan},
            }

            data_bandara = {"pelabuhan": {
                "arah": "kiri", "jarak": "16km",
                "status": status_pelabuhan,
                "eta": hitung_eta(16, status_pelabuhan)
            }}

            data_pelabuhan = {"bandara": {
                "arah": "kanan", "jarak": "7km",
                "status": status_bandara,
                "eta": hitung_eta(7, status_bandara)
            }}

            duration = trafic_duration(eta_bandara, eta_pelabuhan)
            data_lampu = {
                "lampu": {
                    "ke_bandara": duration["bandara"],
                    "ke_pelabuhan": duration["pelabuhan"]
                }
            }

            # Mengirim setiap 3 detik
            if time.time() - waktu_kirim > 3:
                send_json(serial_con, "palang_kota", data_palangkota)
                send_json(serial_con, "palang_bandara", data_bandara)
                send_json(serial_con, "palang_pelabuhan", data_pelabuhan)
                send_json(serial_con, "trafic_light", data_lampu)

                waktu_kirim = time.time()

            if cv2.waitKey(1) & 0xFF == 27:
                break

    finally:
        for cam in cams:
            cam.release()
        cv2.destroyAllWindows()
        print("[Selesai]")


if __name__ == "__main__":
    main()
