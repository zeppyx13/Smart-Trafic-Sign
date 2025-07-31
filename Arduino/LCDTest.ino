#include <wire.h>
#include <adafruit_gfx.h>
#include <adafruit_SSD1306.h>

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

Void Setup() {
  Serial.begin(9600);
  while (!Serial) {
    ;
  }

  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println(F("Gagal memulai OLED"));
    for (;;);
  }

  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(WHITE);
  display.setCursor(0, 0);
  display.println("LCD Test");
  display.display();
}

Void Loop() {
  if (Serial.available()) {
    String inputData = Serial.readStringUntil('\n');
    parseData(inputData);
  }
}