String inputData = "";

void setup() {
  Serial.begin(9600);
  while (!Serial) ;
  Serial.println("Siap menerima data...");
}

void loop() {
  while (Serial.available()) {
    char c = Serial.read();
    if (c == '\n') {
      parseData(inputData);
      inputData = "";  // reset buffer
    } else {
      inputData += c;
    }
  }
}

void parseData(String data) {
  // Contoh: ⬆|Bandara|2|Padat|15;➡|Pelabuhan|3|Lancar|10
  Serial.println("==== DATA MASUK ====");
  int startIdx = 0;
  while (true) {
    int endIdx = data.indexOf(';', startIdx);
    if (endIdx == -1) {
      // Tidak ada data lagi
      endIdx = data.length();
    }

    String segment = data.substring(startIdx, endIdx);
    tampilkanSegment(segment);

    if (endIdx >= data.length()) break;
    startIdx = endIdx + 1;
  }
}

void tampilkanSegment(String segmen) {
  // Split data |
  int idx1 = segmen.indexOf('|');
  int idx2 = segmen.indexOf('|', idx1 + 1);
  int idx3 = segmen.indexOf('|', idx2 + 1);
  int idx4 = segmen.indexOf('|', idx3 + 1);

  if (idx4 == -1) {
    Serial.println("Format tidak valid");
    return;
  }

  String arah = segmen.substring(0, idx1);
  String tujuan = segmen.substring(idx1 + 1, idx2);
  String jarak = segmen.substring(idx2 + 1, idx3);
  String status = segmen.substring(idx3 + 1, idx4);
  String waktu = segmen.substring(idx4 + 1);

  Serial.print("Arah: ");
  Serial.println(arah);
  Serial.print("Tujuan: ");
  Serial.println(tujuan);
  Serial.print("Jarak: ");
  Serial.println(jarak + " km");
  Serial.print("Status: ");
  Serial.println(status);
  Serial.print("ETA: ");
  Serial.println(waktu + " menit");
  Serial.println("----------------------");
}
