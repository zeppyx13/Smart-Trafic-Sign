import cv2
from ultralytics import YOLO
from config import id_kendaraan, nama_kendaraan
from traffic_logic import status_lalu_lintas

model = YOLO("yolov8n.pt")

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
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                        (0, 255, 0), 2)

    status = status_lalu_lintas(jumlah)
    teks = f"{label_arah}: {status} ({jumlah})"
    cv2.putText(frame, teks, (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                0.7, (255, 0, 0), 2)

    return frame, status
