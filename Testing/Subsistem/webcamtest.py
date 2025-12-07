import cv2
cam = {
    "kamera 1": cv2.VideoCapture(0),
    "kamera 2": cv2.VideoCapture(3)
}
for key in cam:
    cam[key].set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cam[key].set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

while True:
    for key in cam:
        ret, frame = cam[key].read()
        if ret:
            cv2.imshow(key, frame)
        else:
            print(f"Gagal membaca dari {key}")
    if cv2.waitKey(1) & 0xFF == 27:
        break
for key in cam:
    cam[key].release()
cv2.destroyAllWindows()
