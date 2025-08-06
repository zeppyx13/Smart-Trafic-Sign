#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <ArduinoJson.h>

// Inisialisasi LCD I2C, biasanya alamat 0x27 atau 0x3F
LiquidCrystal_I2C lcd(0x27, 20, 4);

const char* DEVICE_NAME = "kota";  // <-- Ubah sesuai: "kota", "bandara", atau "pelabuhan"
String inputString = "";

void setup() {
  Serial.begin(9600);
  lcd.init();
  lcd.backlight();
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Menunggu data...");
}

void loop() {
  while (Serial.available()) {
    char c = Serial.read();
    if (c == '\n') {
      processData(inputString);
      inputString = "";
    } else {
      inputString += c;
    }
  }
}

// Fungsi untuk memproses JSON
void processData(String jsonData) {
  StaticJsonDocument<256> doc;
  DeserializationError error = deserializeJson(doc, jsonData);

  if (error) {
    Serial.println("JSON Error");
    return;
  }

  const char* nama = doc["nama"];
  int jumlah = doc["jumlah"];
  const char* status = doc["status"];
  int eta = doc["eta"];

  // Tampilkan ke LCD
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Device: ");
  lcd.print(DEVICE_NAME);

  lcd.setCursor(0, 1);
  lcd.print("Nama: ");
  lcd.print(nama);

  lcd.setCursor(0, 2);
  lcd.print("Jumlah: ");
  lcd.print(jumlah);

  lcd.setCursor(0, 3);
  lcd.print(status);
  lcd.print(" ETA: ");
  lcd.print(eta);
  lcd.print("m");
}
