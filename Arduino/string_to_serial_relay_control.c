#include <string.h>

const byte numChars = 32;
char receivedChars[numChars]; // an array to store the received data

boolean newData = false;
int INA = 2;
int INB = 3;
int INC = 4;
int IND = 5;

void setup() {
  pinMode(INA , OUTPUT);
  pinMode(INB , OUTPUT);
  pinMode(INC , OUTPUT);
  pinMode(IND , OUTPUT);
  
  //initialize relays to be normally off
  digitalWrite(INA, HIGH);
  digitalWrite(INB, HIGH);
  digitalWrite(INC, HIGH);
  digitalWrite(IND, HIGH);
  
  Serial.begin(115200);
}

void loop() {
  recvWithEndMarker();
  showNewData();
}

void recvWithEndMarker() {
  static byte ndx = 0;
  char endMarker = '\n';
  char rc;
 
  // if (Serial.available() > 0) {
  while (Serial.available() > 0 && newData == false) {
    rc = Serial.read();

    if (rc != endMarker) {
      receivedChars[ndx] = rc;
      ndx++;
      if (ndx >= numChars) {
        ndx = numChars - 1;
      }
    }
    else {
      receivedChars[ndx] = '\0'; // terminate the string
      ndx = 0;
      newData = true;
    }
  }
}

void showNewData() {
  if (newData == true) {
    Serial.println(receivedChars);
    
    if( strcmp(receivedChars,"IN1_ON") == 0)
    {
      digitalWrite(INA, LOW);
      Serial.println("IN1 is on");
    }
    else if(strcmp(receivedChars,"IN1_OFF") == 0)
    {
      digitalWrite(INA, HIGH);
      Serial.println("IN1 is off");
    }
    else if(strcmp(receivedChars,"IN2_ON") == 0)
    {
      digitalWrite(INB, LOW);
      Serial.println("IN2 is on");
    }
    else if(strcmp(receivedChars,"IN2_OFF") == 0)
    {
      digitalWrite(INB, HIGH);
      Serial.println("IN2 is off");
    }
    else if(strcmp(receivedChars,"IN3_ON") == 0)
    {
      digitalWrite(INC, LOW);
      Serial.println("IN3 is on");
    }
    else if(strcmp(receivedChars,"IN3_OFF") == 0)
    {
      digitalWrite(INC, HIGH);
      Serial.println("IN3 is off");
    }
    else if(strcmp(receivedChars,"IN4_ON") == 0)
    {
      digitalWrite(IND, LOW);
      Serial.println("IN4 is on");
    }
    else if(strcmp(receivedChars,"IN4_OFF") == 0)
    {
      digitalWrite(IND, HIGH);
      Serial.println("IN4 is off");
    }
    else
      Serial.println("String command not recognized");

    newData = false;
  }
}
