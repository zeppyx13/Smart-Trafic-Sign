import cv2

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Webcam gak mau  kleng!")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        continue

    cv2.imshow("Tes Webcam", frame)

    if cv2.waitKey(1) & 0xFF == 27: #ESC untuk keluar
        break

cap.release()
cv2.destroyAllWindows()
