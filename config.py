# config.py
ports = {
    "palang_kota": 'COM14',
    "palang_pelabuhan": 'COM15',
    "palang_bandara": 'COM16',
    "trafic_light": 'COM21'
}

baud_rate = 9600

model_path = "yolov8n.pt"

id_kendaraan = [2, 3, 5, 7]
nama_kendaraan = {
    2: 'Car',
    3: 'Motor',
    5: 'Bus',
    7: 'Truck'
}
