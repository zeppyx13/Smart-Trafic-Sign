#include <ArduinoJson.h>

// Pin lampu LED: urutannya [Merah, Kuning, Hijau]
const int lampuKotaLurus[]  = {2, 3, 4};   // Menuju Pelabuhan
const int lampuKotaBelok[]  = {5, 6, 7};   // Menuju Bandara
const int lampuPelabuhan[]  = {8, 9, 10};  // Menuju Bandara
const int lampuBandara[]    = {11, 12, 13}; // Menuju Pelabuhan

// Status lalu lintas dari Raspberry Pi
String statusBandara = "lancar";
String statusPelabuhan = "lancar";

unsigned long lastMillis = 0;
int fase = 0;

void setup() {
  Serial.begin(9600);

  // Inisialisasi pin sebagai OUTPUT
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
    String input = Serial.readStringUntil('\n');
    parseData(input);
  }

  // Atur logika traffic berdasarkan waktu
  aturTrafficBerdasarkanStatus();
}

// Fungsi parsing JSON dari Raspberry Pi
void parseData(String jsonData) {
  StaticJsonDocument<512> doc;
  DeserializationError error = deserializeJson(doc, jsonData);

  if (error) {
    Serial.println("Gagal parsing JSON!");
    return;
  }

  statusBandara = doc["palang_kota"]["bandara"]["status"] | "lancar";
  statusPelabuhan = doc["palang_kota"]["pelabuhan"]["status"] | "lancar";

  Serial.print("Bandara: "); Serial.println(statusBandara);
  Serial.print("Pelabuhan: "); Serial.println(statusPelabuhan);
}

// Mendapatkan durasi hijau berdasarkan status
int durasiHijau(String status) {
  if (status == "macet") return 60;
  if (status == "padat") return 45;
  if (status == "sedang") return 30;
  return 20;  // lancar
}

// Logika pergantian traffic light siklus penuh
void aturTrafficBerdasarkanStatus() {
  static unsigned long tStart = millis();
  static int tahap = 0;
  static int durasi = 0;

  if (millis() - tStart >= durasi * 1000UL) {
    matikanSemuaLampu();

    switch (tahap) {
      case 0:
        // Kota ke Pelabuhan
        nyalakanHijau(lampuKotaLurus);
        durasi = durasiHijau(statusPelabuhan);
        break;
      case 1:
        nyalakanKuning(lampuKotaLurus);
        durasi = 3;
        break;
      case 2:
        // Kota ke Bandara
        nyalakanHijau(lampuKotaBelok);
        durasi = durasiHijau(statusBandara);
        break;
      case 3:
        nyalakanKuning(lampuKotaBelok);
        durasi = 3;
        break;
      case 4:
        // Pelabuhan ke Bandara
        nyalakanHijau(lampuPelabuhan);
        durasi = durasiHijau(statusBandara);
        break;
      case 5:
        nyalakanKuning(lampuPelabuhan);
        durasi = 3;
        break;
      case 6:
        // Bandara ke Pelabuhan
        nyalakanHijau(lampuBandara);
        durasi = durasiHijau(statusPelabuhan);
        break;
      case 7:
        nyalakanKuning(lampuBandara);
        durasi = 3;
        break;
    }

    tStart = millis();
    tahap = (tahap + 1) % 8;
  }
}

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

void nyalakanKuning(const int lampu[]) {
  digitalWrite(lampu[0], LOW);
  digitalWrite(lampu[1], HIGH);
  digitalWrite(lampu[2], LOW);
}

void nyalakanMerah(const int lampu[]) {
  digitalWrite(lampu[0], HIGH);
  digitalWrite(lampu[1], LOW);
  digitalWrite(lampu[2], LOW);
}
