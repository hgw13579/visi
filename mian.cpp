
#include <SoftwareSerial.h>

int RX = 7; 
int TX = 8; 
SoftwareSerial bluetooth(RX, TX);

int vibratorPin = 9; 
int buttonPin1 = 2; 
int buttonPin2 = 12;

int vibrationIntensity = 50; 
bool buttonState1 = HIGH;
bool lastButtonState1 = HIGH; 
bool buttonState2 = HIGH; 
bool lastButtonState2 = HIGH; 

void setup() {
  pinMode(vibratorPin, OUTPUT);
  pinMode(buttonPin1, INPUT_PULLUP);
  pinMode(buttonPin2, INPUT_PULLUP); 

  Serial.begin(9600);
  bluetooth.begin(9600);
}

void loop() {
  buttonState1 = digitalRead(buttonPin1);
  buttonState2 = digitalRead(buttonPin2);
  if (buttonState1 == LOW && lastButtonState1 == HIGH) {
    changeVibrationIntensity(true);
    vibrateButtonPress();
  }
  
  if (buttonState2 == LOW && lastButtonState2 == HIGH) {
    changeVibrationIntensity(false);
    vibrateButtonPress();
  }
  
  lastButtonState1 = buttonState1;
  lastButtonState2 = buttonState2;

  if (bluetooth.available()) {
    char data = bluetooth.read();
    Serial.write(data);

    if (data == 'F') {
      Serial.print("FIND from Raspberry Pi");
      analogWrite(vibratorPin, vibrationIntensity);
      delay(1000);
      analogWrite(vibratorPin, 0); 
      Serial.print("The intensity of vibration when receiving F");
      Serial.println(vibrationIntensity); 
    } else if (data == 'G') {
      Serial.print("Raspberry Pi signaled GO");
      for (int i = 0; i < 2; i++) {
        analogWrite(vibratorPin, vibrationIntensity);
        delay(500); 
        analogWrite(vibratorPin, 0);
        delay(500); 
        Serial.print("The intensity of vibration when receiving G");
        Serial.println(vibrationIntensity); 
      }
    }
  }
  
  if (Serial.available()) {
    bluetooth.write(Serial.read());
  }
}

void vibrateButtonPress() {
  Serial.print("Current Vibration Strength");
  Serial.println(vibrationIntensity); 
  analogWrite(vibratorPin, vibrationIntensity); 
  delay(250); 
  analogWrite(vibratorPin, 0); 
}

void changeVibrationIntensity(bool increase) {
  if (increase) {
    vibrationIntensity += 25; 
    if (vibrationIntensity > 250) {
      vibrationIntensity = 250; 
    }
  } else {
    vibrationIntensity -= 25; 
    if (vibrationIntensity < 50) {
      vibrationIntensity = 50; 
    }
  }
}
