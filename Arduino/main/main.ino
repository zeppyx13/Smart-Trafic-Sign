#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_ADDR 0x3C
#define TCA_ADDR 0x70

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire);

// Pilih channel pada TCA9548A
void tca_select(uint8_t channel) {
  if (channel > 7) return;
  Wire.beginTransmission(TCA_ADDR);
  Wire.write(1 << channel);
  Wire.endTransmission();
}

// Inisialisasi OLED
void inisialisasiOLED(uint8_t channel, const char* nama) {
  tca_select(channel);
  if (!display.begin(SSD1306_SWITCHCAPVCC, OLED_ADDR)) {
    Serial.print("Gagal OLED di channel ");
    Serial.println(channel);
  } else {
    display.clearDisplay();
    display.setTextSize(1);
    display.setTextColor(SSD1306_WHITE);
    display.setCursor(0, 0);
    display.println(nama);
    display.display();
  }
}

// Menampilkan data di OLED tertentu
void tampilkanOLED(uint8_t channel, const String &arah, const String &tujuan, const String &jalur, const String &status, const String &eta) {
  tca_select(channel);
  display.clearDisplay();
  display.setTextSize(1);
  display.setCursor(0, 0);
  display.println("Arah   : " + arah);
  display.println("Tujuan : " + tujuan);
  display.println("Jalur  : " + jalur);
  display.println("Status : " + status);
  display.println("ETA    : " + eta + " mnt");
  display.display();
}

void setup() {
  Serial.begin(9600);
  Wire.begin();
  inisialisasiOLED(0, "OLED Bandara");
  inisialisasiOLED(1, "OLED Pelabuhan");
}

void loop() {
  static String buffer = "";

  while (Serial.available()) {
    char c = Serial.read();
    if (c == '\n') {
      // Contoh data: ⬆|Bandara|2|Padat|15;➡|Pelabuhan|3|Lancar|10
      int start = 0;
      while (true) {
        int end = buffer.indexOf(';', start);
        if (end == -1) break;

        String segmen = buffer.substring(start, end);
        start = end + 1;

        int p1 = segmen.indexOf('|');
        int p2 = segmen.indexOf('|', p1 + 1);
        int p3 = segmen.indexOf('|', p2 + 1);
        int p4 = segmen.indexOf('|', p3 + 1);

        if (p1 > 0 && p2 > p1 && p3 > p2 && p4 > p3) {
          String arah = segmen.substring(0, p1);
          String tujuan = segmen.substring(p1 + 1, p2);
          String jalur = segmen.substring(p2 + 1, p3);
          String status = segmen.substring(p3 + 1, p4);
          String eta = segmen.substring(p4 + 1);

          // Cek tujuan dan kirim ke OLED yang sesuai
          if (tujuan.equalsIgnoreCase("Bandara")) {
            tampilkanOLED(0, arah, tujuan, jalur, status, eta);
          } else if (tujuan.equalsIgnoreCase("Pelabuhan")) {
            tampilkanOLED(1, arah, tujuan, jalur, status, eta);
          }
        }
      }
      buffer = "";
    } else {
      buffer += c;
    }
  }
}
