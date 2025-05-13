

/*
Fil: robot_arm_arduino
Författare: Figge Hellström och Hannes Viktor
Datum: 2025-05-13
ROBOTARM KOMMANDO MOTTAGARE

Beskrivning:
Koden tar emot kommando via serial port och översätter det till vinklar för olika servomotorer
*/


#include <Servo.h>

// Skapa Servo-objekt för varje motor
Servo servoVertical;   // Används för pin 9 (vertikal)
Servo servoHorizontal; // Används för pin 10 (horisontell)
Servo servoGrip;       // Används för pin 11 (grepp)

// Variabel för indata från Serial
String serialInput = "";

void setup() {
  // Starta seriell kommunikation med 9600 baud
  Serial.begin(9600);
  
  // Koppla servon till rätt pinnar
  servoVertical.attach(9);
  servoHorizontal.attach(10);
  servoGrip.attach(11);
}

void loop() {
  // Kontrollera om data finns tillgänglig på Serial
  while (Serial.available() > 0) {
    char inChar = (char)Serial.read();
    
    // Om vi får en newline (\n) betyder det att kommandot är komplett
    if (inChar == '\n') {
      serialInput.trim();  // Ta bort eventuella blanksteg i början/slutet
      
      // Om vi fått ett tomt meddelande hoppar vi över
      if (serialInput.length() > 0) {
        // Leta efter kolon (:) som separerar pin och vinkel
        int separatorIndex = serialInput.indexOf(':');
        if (separatorIndex != -1) {
          String pinStr = serialInput.substring(0, separatorIndex);
          String angleStr = serialInput.substring(separatorIndex + 1);
          
          int pin = pinStr.toInt();
          int angle = angleStr.toInt();
          
          // Begränsa vinkeln mellan 0 och 180 grader
          angle = constrain(angle, 0, 180);

          // Styr rätt servo beroende på angiven pin
          if (pin == 9) {
            servoVertical.write(angle);
          }
          else if (pin == 10) {
            servoHorizontal.write(angle);
          }
          else if (pin == 11) {
            servoGrip.write(angle);
          }
        }
      }
      // Nollställ serialInput för nästa kommando
      serialInput = "";
    }
    else {
      // Samla in tecken till kommandosträngen
      serialInput += inChar;
    }
  }
}