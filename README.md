
# SIGMA (Smart Integrated Guidance for Mobility & Awareness)

Smart Traffic Sign Berbasis Pengenalan Kendaraan dan AI untuk Manajemen Lalu Lintas Dinamis merupakan sistem cerdas yang memanfaatkan teknologi computer vision dan Machine Learning untuk mendeteksi jenis serta jumlah kendaraan secara real-time melalui kamera. Informasi ini diproses untuk menentukan kondisi lalu lintas (lancar, padat, atau macet), kemudian ditampilkan secara dinamis melalui papan jalan elektronik (smart sign). Sistem ini bertujuan untuk membantu pengemudi mengambil keputusan rute secara lebih efisien dan responsif terhadap situasi aktual di lapangan.

## 🧪Features

- Multiple Camera
- Realtime Monitoring
- Fully Modular
- Arduino Integration
- Dynamic Traffic Sign Display
## ⚙️Installation


### 1. Clone Repository

```bash
git clone https://github.com/zeppyx13/Smart-Trafic-Sign
cd smart-traffic-sign
```


### 2. Install Dependencies

```bash
pip install opencv-python ultralytics pyserial
```

### 4. Download YOLOv8 Model

Download model YOLOv8 pre-trained dari [Ultralytics](https://github.com/ultralytics/ultralytics):

```bash
https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt
```

Atau bisa langsung menggunakan nama `yolov8n.pt` jika sudah tersedia otomatis saat pemanggilan YOLO lewat `ultralytics`.

### 5. Hubungkan Hardware

* Sambungkan webcam ke port USB.
* Sambungkan Arduino ke port COM dan pastikan menggunakan baud rate (default: 9600).
* Cek port Arduino dengan Device Manager.

### 6. Jalankan Program

```bash
python main.py
```
