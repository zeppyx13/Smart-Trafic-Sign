import serial
import time

arduino_port = 'COM7'  #Ardduino Port
baud_rate = 9600

try:
    ser = serial.Serial(arduino_port, baud_rate, timeout=1)
    time.sleep(2)

    data_pelang = "⬆|Bandara|2|Padat|15;➡|Pelabuhan|3|Lancar|10\n"

    print("Mulai komunikasi dengan Arduino di", arduino_port)
    while True:
        # Kirim data ke Arduino
        ser.write(data_pelang.encode())
        print("Terkirim:", data_pelang.strip())

        # Arduino Response
        while ser.in_waiting > 0:
            line = ser.readline().decode('utf-8', errors='replace').strip()
            if line:
                print("Dari Arduino:", line)

        time.sleep(5)

except KeyboardInterrupt:
    print("\nDihentikan oleh user.")

except Exception as e:
    print("Terjadi error:", e)

finally:
    if 'ser' in locals() and ser.is_open:
        ser.close()
    print("Koneksi serial ditutup.")
