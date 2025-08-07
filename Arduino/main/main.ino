#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <ArduinoJson.h>

// Atur lokasi palang: "kota", "bandara", atau "pelabuhan"
#define PALANG_LOKASI "kota"

// Inisialisasi LCD 20x4
LiquidCrystal_I2C lcd(0x27, 20, 4);

// Karakter panah custom
byte arrowStraight[8] = {
  0b00100, 0b00100, 0b01110, 0b10101,
  0b00100, 0b00100, 0b00100, 0b00000
};

byte arrowLeftTurn[8] = {
  0b00100, 0b01000, 0b11110, 0b01001,
  0b00110, 0b00000, 0b00000, 0b00000
};

byte arrowRightTurn[8] = {
  0b00100, 0b00010, 0b01111, 0b10010,
  0b01100, 0b00000, 0b00000, 0b00000
};

unsigned long lastDataTime = 0;
const unsigned long timeout = 5000;

// Buffer pembacaan serial
String jsonBuffer = "";

void setup() {
  Serial.begin(9600);
  lcd.init();
  lcd.backlight();

  lcd.createChar(0, arrowStraight);
  lcd.createChar(1, arrowLeftTurn);
  lcd.createChar(2, arrowRightTurn);

  tampilkanMenunggu();
}

void loop() {
  while (Serial.available()) {
    char c = Serial.read();
    if (c == '\n') {
      processJson(jsonBuffer);
      jsonBuffer = ""; // reset buffer
    } else {
      jsonBuffer += c;
      if (jsonBuffer.length() > 1024) {
        // Data terlalu panjang, reset
        jsonBuffer = "";
      }
    }
  }

  if (millis() - lastDataTime > timeout) {
    tampilkanMenunggu();
    lastDataTime = millis(); // supaya tidak terus-terusan refresh
  }
}

void processJson(String jsonStr) {
  StaticJsonDocument<1024> doc;
  DeserializationError error = deserializeJson(doc, jsonStr);
  if (error) {
    lcd.clear();
    lcd.setCursor(5, 1);
    lcd.print("Tetap Fokus");
    lcd.setCursor(3, 2);
    lcd.print("Dalam Berkendara");
    delay(2000);
    return;
  }

  lcd.clear();

  if (strcmp(PALANG_LOKASI, "kota") == 0) {
    if (doc.containsKey("bandara")) {
      tampilkanTujuan("Bandara", doc["bandara"].as<JsonObject>());
    }
    if (doc.containsKey("pelabuhan")) {
      tampilkanTujuan("Pelabuhan", doc["pelabuhan"].as<JsonObject>());
    }
  } else if (strcmp(PALANG_LOKASI, "bandara") == 0) {
    if (doc.containsKey("pelabuhan")) {
      tampilkanTujuan("Pelabuhan", doc["pelabuhan"].as<JsonObject>());
    }
  } else if (strcmp(PALANG_LOKASI, "pelabuhan") == 0) {
    if (doc.containsKey("bandara")) {
      tampilkanTujuan("Bandara", doc["bandara"].as<JsonObject>());
    }
  }

  lastDataTime = millis();
}

void tampilkanTujuan(const char* nama, JsonObject data) {
  if (!data.isNull()) {
    String arah = data["arah"] | "";
    String jarak = data["jarak"] | "";
    String status = data["status"] | "";
    String eta = data["eta"] | "";
    String alternatif = data["alternatif"] | "";

    // Halaman utama
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.write(getArrowCode(arah));
    lcd.print(" ");
    lcd.print(nama);
    lcd.print(" ");
    lcd.print(jarak);

    lcd.setCursor(0, 1);
    lcd.print("--------------------");

    lcd.setCursor(0, 2);
    lcd.print("Status : ");
    lcd.print(status);

    lcd.setCursor(0, 3);
    lcd.print("ETA    : ");
    lcd.print(eta);
    lcd.print(" mnt");

    delay(4000);

    // Halaman alternatif arah
    status.toLowerCase();
    if ((status == "padat" || status == "macet") && alternatif.length() > 0) {
      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("Alternatif Arah:");
      lcd.setCursor(0, 1);
      lcd.print("--------------------");

      lcd.setCursor(0, 2);
      if (alternatif.length() > 20) {
        lcd.print(alternatif.substring(0, 20));
        lcd.setCursor(0, 3);
        lcd.print(alternatif.substring(20));
      } else {
        lcd.print(alternatif);
        lcd.setCursor(0, 3);
        lcd.print("> Coba rute lain");
      }

      delay(4000);
    }
  }
}

byte getArrowCode(String arah) {
  arah.toLowerCase();
  if (arah == "lurus") return 0;
  else if (arah == "kiri" || arah == "belok kiri") return 1;
  else if (arah == "kanan" || arah == "belok kanan") return 2;
  else return 0;
}

void tampilkanMenunggu() {
  lcd.clear();
  lcd.setCursor(2, 1);
  lcd.print("Menunggu data...");
}
