#include <ArduinoJson.h>

// Pin lampu LED: [Merah, Kuning, Hijau]
const int lampuKotaLurus[]  = {2, 3, 4};   // Menuju Pelabuhan
const int lampuKotaBelok[]  = {5, 6, 7};   // Menuju Bandara
const int lampuPelabuhan[]  = {8, 9, 10};  // Menuju Bandara
const int lampuBandara[]    = {11, 12, 13}; // Menuju Pelabuhan

// default durations in seconds
int durasi_ke_bandara = 20;
int durasi_ke_pelabuhan = 20;

void setup() {
  Serial.begin(9600);

  for (int i = 0; i < 3; i++) {
    pinMode(lampuKotaLurus[i], OUTPUT);
    pinMode(lampuKotaBelok[i], OUTPUT);
    pinMode(lampuPelabuhan[i], OUTPUT);
    pinMode(lampuBandara[i], OUTPUT);
  }

  matikanSemuaLampu();
}

void loop() {
  if (Serial.available()) {
    String jsonData = Serial.readStringUntil('\n');
    parseJson(jsonData);
  }

  jalankanSiklusLampu();
}

// parsing JSON
void parseJson(String input) {
  StaticJsonDocument<256> doc;
  DeserializationError error = deserializeJson(doc, input);

  if (error) {
    Serial.println("Gagal parsing JSON!");
    return;
  }

  durasi_ke_bandara = doc["lampu"]["ke_bandara"] | 20;
  durasi_ke_pelabuhan = doc["lampu"]["ke_pelabuhan"] | 20;

  Serial.print("Durasi ke Bandara: "); Serial.println(durasi_ke_bandara);
  Serial.print("Durasi ke Pelabuhan: "); Serial.println(durasi_ke_pelabuhan);
}

void jalankanSiklusLampu() {
  static int tahap = 0;
  static unsigned long lastMillis = 0;
  static int durasi = 0;

  if (millis() - lastMillis >= durasi * 1000UL) {
    matikanSemuaLampu();

    // Nyalakan lampu merah untuk semua rute
    nyalakanMerah(lampuKotaLurus);
    nyalakanMerah(lampuKotaBelok);
    nyalakanMerah(lampuPelabuhan);
    nyalakanMerah(lampuBandara);

    switch (tahap) {
      case 0:  // Kota -> Pelabuhan
        nyalakanHijau(lampuKotaLurus);
        durasi = durasi_ke_pelabuhan;
        break;
      case 1:
        nyalakanKuning(lampuKotaLurus);
        durasi = 3;
        break;
      case 2:  // Kota -> Bandara
        nyalakanHijau(lampuKotaBelok);
        durasi = durasi_ke_bandara;
        break;
      case 3:
        nyalakanKuning(lampuKotaBelok);
        durasi = 3;
        break;
      case 4: // Pelabuhan -> Bandara
        nyalakanHijau(lampuPelabuhan);
        durasi = durasi_ke_bandara;
        break;
      case 5:
        nyalakanKuning(lampuPelabuhan);
        durasi = 3;
        break;
      case 6: // Bandara -> Pelabuhan
        nyalakanHijau(lampuBandara);
        durasi = durasi_ke_pelabuhan;
        break;
      case 7:
        nyalakanKuning(lampuBandara);
        durasi = 3;
        break;
    }

    tahap = (tahap + 1) % 8;
    lastMillis = millis();
  }
}

// turn off all lights
void matikanSemuaLampu() {
  for (int i = 0; i < 3; i++) {
    digitalWrite(lampuKotaLurus[i], LOW);
    digitalWrite(lampuKotaBelok[i], LOW);
    digitalWrite(lampuPelabuhan[i], LOW);
    digitalWrite(lampuBandara[i], LOW);
  }
}

void nyalakanHijau(const int lampu[]) {
  digitalWrite(lampu[0], LOW);
  digitalWrite(lampu[1], LOW);
  digitalWrite(lampu[2], HIGH);
}

// set kuning on
void nyalakanKuning(const int lampu[]) {
  digitalWrite(lampu[0], LOW);
  digitalWrite(lampu[1], HIGH)
  digitalWrite(lampu[2], LOW);
}

// set merah on
void nyalakanMerah(const int lampu[]) {
  digitalWrite(lampu[0], HIGH);
  digitalWrite(lampu[1], LOW);
  digitalWrite(lampu[2], LOW);
}