#include <Servo.h>

//Intruder Prevention Project
// 문제 및 해결방안 : 버튼이 잘 안눌려서 저항을 약하게 함. 

#define BUZZER 8
#define R_LED 9
#define G_LED 10
#define B_LED 11
#define SECRET_BUTTON4 5
#define SECRET_BUTTON3 6
#define SECRET_BUTTON2 7
#define SECRET_BUTTON1 12
#define SENSOR_TRIG 2
#define SENSOR_ECHO 3
#define RESET A0

int number1 = 0, number2 = 0, number3 = 0, number4 = 0;
int touch_start = 500;
String condition = "WRONG";

void setup() {
  // put your setup code here, to run once:
  pinMode(SENSOR_TRIG, OUTPUT);
  pinMode(SENSOR_ECHO, INPUT);

  // 아날로그는 초기화안해도 됨.

  pinMode(SECRET_BUTTON1, INPUT);
  pinMode(SECRET_BUTTON2, INPUT);
  pinMode(SECRET_BUTTON3, INPUT);
  pinMode(SECRET_BUTTON4, INPUT);

  Serial.begin(9600);
}

void loop() {
  //단순 통신
  Serial.println("Hello, dohee!");
  // put your main code here, to run repeatedly:
  digitalWrite(SENSOR_TRIG, HIGH);
  delayMicroseconds(2);
  digitalWrite(SENSOR_TRIG, HIGH);
  delayMicroseconds(10);
  digitalWrite(SENSOR_TRIG, LOW); // 초음파센서 초기화를 위해 계속 껐다, 켰다 하는 것.
  long distance = pulseIn(SENSOR_ECHO, HIGH)/58.2 ;

  analogWrite(R_LED, 0);
  analogWrite(B_LED, 0);
  analogWrite(G_LED, 255);
  delay(100);

  if (distance >= 20) { // 문에 있는 특정 장치와 거리가 멀어지면 소리가 남.
    Serial.println("There is an intruder. You should check it!");
    delay(100);
    while (1) {
      analogWrite(R_LED, 255);
      analogWrite(G_LED, 0);
      analogWrite(B_LED, 0);

      tone(8, 1500, 20) ;
	    delay(100);
	    tone(8, 1500, 20) ; 
	    delay(distance);

      int i = analogRead(RESET);
      
      if (i < touch_start) {
        number1 = 0, number2= 0, number3 = 0, number4 = 0;
        Serial.print("AFTER TOUCH : ");
        Serial.println(i);
        analogWrite(R_LED, 0);
        analogWrite(B_LED, 0);
        analogWrite(G_LED, 255);
        delay(100);
        continue;
      } 

      if (digitalRead(SECRET_BUTTON1) == HIGH) {
        ++number1; 
      }
      if (digitalRead(SECRET_BUTTON2) == HIGH) {
        ++number2; 
      } 
      if (digitalRead(SECRET_BUTTON3) == HIGH) {
        ++number3; 
      }
      if (digitalRead(SECRET_BUTTON4) == HIGH) {
        ++number4; 
      }

      if (number1 == 1 && number2 == 1 && number3 == 2 && number4 == 6) {
        condition = "CORRECT";
        goto outside1;
      }

      Serial.print("number1 : ");
      Serial.print(number1);
      Serial.print(" number2 : ");
      Serial.print(number2 );
      Serial.print(" number3 : ");
      Serial.print(number3 );
      Serial.print(" number4 : ");
      Serial.println(number4+1 );

      i = analogRead(RESET);
    } 
  }

  outside1 : // 비밀번호가 맞았을 경우
  while(condition == "CORRECT") {
    analogWrite(R_LED, 0);
    analogWrite(B_LED, 0);
    analogWrite(G_LED, 255);
  };
}
