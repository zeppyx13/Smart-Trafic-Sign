#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64


#define TCA9548A_ADDR 0x70
#define OLED_ADDR 0x3C

Adafruit_SSD1306 display1(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);
Adafruit_SSD1306 display2(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);

void tcaSelect(uint8_t channel) {
  if (channel > 7) return;
  Wire.beginTransmission(TCA9548A_ADDR);
  Wire.write(1 << channel);
  Wire.endTransmission();
}

void setup() {
  Wire.begin();
  Serial.begin(9600);

  tcaSelect(0);
  if (!display1.begin(SSD1306_SWITCHCAPVCC, OLED_ADDR)) {
    Serial.println("OLED 1 gagal");
    while (1);
  }
  display1.clearDisplay();
  display1.setTextSize(1);
  display1.setTextColor(SSD1306_WHITE);
  display1.setCursor(0, 0);
  display1.println("pelabuhan 5km padat");
  display1.display();

  tcaSelect(1);
  if (!display2.begin(SSD1306_SWITCHCAPVCC, OLED_ADDR)) {
    Serial.println("OLED 2 gagal");
    while (1);
  }
  display2.clearDisplay();
  display2.setTextSize(1);
  display2.setTextColor(SSD1306_WHITE);
  display2.setCursor(0, 0);
  display2.println("bandara 10km lancar");
  display2.display();
}

void loop() {
  tcaSelect(0);
  display1.clearDisplay();
  display1.setCursor(0, 20);
  display1.setTextSize(2);
  display1.println("OLED 1 OK");
  display1.display();

  delay(1000);

  tcaSelect(1);
  display2.clearDisplay();
  display2.setCursor(0, 20);
  display2.setTextSize(2);
  display2.println("OLED 2 OK");
  display2.display();

  delay(1000);
}
