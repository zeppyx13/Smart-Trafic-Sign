import time
import board
import busio
import digitalio
import RPi.GPIO as GPIO
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306

# Setup IR sensor pins
IR1_PIN = 17
IR2_PIN = 27

GPIO.setmode(GPIO.BCM)
GPIO.setup(IR1_PIN, GPIO.IN)
GPIO.setup(IR2_PIN, GPIO.IN)

i2c = busio.I2C(board.SCL, board.SDA)

oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)

oled.fill(0)
oled.show()

image = Image.new("1", (oled.width, oled.height))
draw = ImageDraw.Draw(image)
font = ImageFont.load_default()

try:
    while True:
        ir1_status = GPIO.input(IR1_PIN)
        ir2_status = GPIO.input(IR2_PIN)
        draw.rectangle((0, 0, oled.width, oled.height), outline=0, fill=0)

        # Tampilkan status IR ke OLED
        draw.text((0, 0), "Tes IR dan OLED", font=font, fill=255)
        draw.text((0, 20), f"IR1: {'Terhalang' if ir1_status == 0 else 'Bersih'}", font=font, fill=255)
        draw.text((0, 35), f"IR2: {'Terhalang' if ir2_status == 0 else 'Bersih'}", font=font, fill=255)

        # Tampilkan ke layar
        oled.image(image)
        oled.show()
        print(f"IR1: {'TERHALANG' if ir1_status == 0 else 'Bersih'}, IR2: {'TERHALANG' if ir2_status == 0 else 'Bersih'}")

        time.sleep(0.5)

except KeyboardInterrupt:
    print("Berhenti...")
    oled.fill(0)
    oled.show()
    GPIO.cleanup()
