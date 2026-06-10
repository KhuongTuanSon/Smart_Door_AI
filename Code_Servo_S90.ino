#include <Servo.h>
#include <LiquidCrystal_I2C.h>
#include <Wire.h>

// khởi tạo đối tượng
Servo doorServo;
LiquidCrystal_I2C lcd(0x27 ,16 ,2);

// define chan cam 
const int servoPin =  5;
const int buzzerPin = 8;
const int ledGreen = 11;
const int ledRed = 12;
const int ledRed2 = 6;

// bien trang thai cua
bool isDoorOpen = false;

void setup (){
  Serial.begin(9600);

  doorServo.attach(servoPin);// day la giao thuc voiw servo
  doorServo.write(0);

  pinMode(buzzerPin, OUTPUT);
  digitalWrite(buzzerPin, LOW);
  pinMode(ledGreen, OUTPUT);
  pinMode(ledRed, OUTPUT);
  pinMode(ledRed2,OUTPUT);
  digitalWrite(ledRed, HIGH);
  digitalWrite(ledGreen, LOW);
  digitalWrite(ledRed2, HIGH);

  lcd.init();
  lcd.backlight();
  lcd.setCursor(0,0);
  lcd.print("Hello Leader");
  lcd.setCursor(0,1);
  lcd.print("Status: Closed");
}

void loop(){
  if (Serial.available() > 0 ){
    char command = Serial.read();
    if (command == '\n' || command == '\r') return; // lam sach du liẹu

    if (command == '1' && !isDoorOpen){
      openDoor();
      Serial.println("Opened");
    }
    else if (command == '0' && isDoorOpen){
      closeDoor();
      Serial.println("Closed");
    }
  }
}

void openDoor(){
  lcd.clear();
  lcd.setCursor(0,0);
  lcd.print("Welcome, Leader");

  digitalWrite(ledGreen, HIGH);
  digitalWrite(ledRed, LOW);
  digitalWrite(ledRed2, LOW);

  tone(buzzerPin, 2500 ,200);

  // mở cửa (nhảy thẳng)
  doorServo.write(60);
  delay(500); // đợi servo quay xong

  isDoorOpen = true;

  lcd.setCursor(0,1);
  lcd.print("Status: OPENED");
}

void closeDoor(){
  lcd.clear();
  lcd.setCursor(0,0);
  lcd.print("Door is closed");

  digitalWrite(ledGreen, LOW);
  digitalWrite(ledRed, HIGH);
  digitalWrite(ledRed2,HIGH);

  // đóng cửa (nhảy thẳng)
  doorServo.write(0);
  delay(500); // đợi servo quay xong

  isDoorOpen = false;

  lcd.setCursor(0,1);
  lcd.print("Status: Closed");
}