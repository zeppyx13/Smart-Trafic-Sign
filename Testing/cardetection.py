import cv2
from ultralytics import YOLO

# Load model
model = YOLO("../yolov8n.pt")

cams = [
    cv2.VideoCapture(0),  # Webcam 1
    cv2.VideoCapture(2),  # Webcam 2
]

id_kendaraan = [2, 3, 5, 7]
nama_kendaraan = {2: 'Car', 3: 'Motor', 5: 'Bus', 7: 'Truck'}

def status_lalu_lintas(jumlah):
    if jumlah >= 9:
        return "Macet"
    elif jumlah >= 6:
        return "Padat"
    elif jumlah >= 3:
        return "Sedang"
    else:
        return "Lancar"

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

    status = status_lalu_lintas(jumlah)
    teks = f"Arah {cam_index+1}: {status} ({jumlah} kendaraan)"
    print(teks)
    cv2.putText(frame, teks, (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                0.7, (255, 0, 0), 2)

    return frame

try:
    while True:
        for i, cam in enumerate(cams):
            ret, frame = cam.read()
            if not ret:
                print(f"not found webcam {i}")
                continue

            frame = cv2.resize(frame, (640, 480))
            frame = proses_frame(frame, i)
            cv2.imshow(f"webcam {i+1}", frame)

        if cv2.waitKey(1) & 0xFF == 27:  #ESC untuk keluar
            break

except KeyboardInterrupt:
    print("Quitting...")

finally:
    for cam in cams:
        cam.release()
    cv2.destroyAllWindows()
