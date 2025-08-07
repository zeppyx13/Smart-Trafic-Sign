#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <ArduinoJson.h>

// Ganti alamat jika perlu: 0x27 atau 0x3F
LiquidCrystal_I2C lcd(0x27, 20, 4);

// Ganti sesuai lokasi alat: "kota", "bandara", atau "pelabuhan"
const char* DEVICE_NAME = "kota";

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

void processData(String jsonData) {
  StaticJsonDocument<512> doc;
  DeserializationError error = deserializeJson(doc, jsonData);

  if (error) {
    Serial.println("JSON parsing error");
    return;
  }

  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Dev: ");
  lcd.print(DEVICE_NAME);

  if (strcmp(DEVICE_NAME, "kota") == 0) {
    showRow(1, doc["bandara"], "BND");
    showRow(2, doc["pelabuhan"], "PLB");
  } else if (strcmp(DEVICE_NAME, "bandara") == 0) {
    showRow(1, doc["pelabuhan"], "PLB");
  } else if (strcmp(DEVICE_NAME, "pelabuhan") == 0) {
    showRow(1, doc["bandara"], "BND");
  }
}

// Tampilkan satu baris info tujuan
void showRow(int row, JsonVariant data, const char* label) {
  if (!data.isNull()) {
    String status = data["status"] | "null";
    String arah = data["arah"] | "-";
    String jarak = data["jarak"] | "-";
    String eta = data["eta"] | "-";

    lcd.setCursor(0, row);
    lcd.print(label);
    lcd.print(" ");
    lcd.print(status);

    lcd.setCursor(0, row + 1);
    lcd.print(arah);
    lcd.print(" ");
    lcd.print(jarak);
    lcd.print(" ");
    lcd.print(eta);
  }
}
