#include <Keyboard.h>
#include <Adafruit_NeoPixel.h>

#define LED_PIN D3
#define MX_PIN D2
#define LED_COUNT 1

int mxState = 0;

Adafruit_NeoPixel pixel(LED_COUNT, LED_PIN, NEO_GRB + NEO_KHZ800);

bool buttonState = false;
bool lastButtonState = false;
unsigned long debounceDelay = 50;
unsigned long lastDebounceTime = 0;
bool keyPressed = false;

void setup() {
  Serial.begin(115200);
  Keyboard.begin();
  delay(100);
  pinMode(MX_PIN, INPUT_PULLUP);
  pixel.begin();
  pixel.show();            
  pixel.setBrightness(50); 
}

void loop() {
  mxState = digitalRead(MX_PIN);
  if (mxState != lastButtonState) {
    lastDebounceTime = millis();
  }

  if ((millis() - lastDebounceTime) > debounceDelay) {
    if (mxState != buttonState) {
      buttonState = mxState;
      if (buttonState == HIGH) {
        keyPressed = false;
        pixel.setPixelColor(0, pixel.Color(0, 0, 0));
        pixel.show();
      } else {
        if (!keyPressed) {
          pixel.setPixelColor(0, pixel.Color(150, 0, 255));
          pixel.show();

          
          Keyboard.press(KEY_LEFT_CTRL);
          delay(100);
          Keyboard.press(KEY_LEFT_ALT);
          delay(100);
          Keyboard.press('c');
          delay(100);
          Keyboard.releaseAll();
          

          Serial.println("Keys have been pressed");

          keyPressed = true;
        }
      }
    }
  }

  lastButtonState = mxState;
}
