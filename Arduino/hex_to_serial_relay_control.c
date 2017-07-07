#include <string.h>
#define ERROR -1
#define OFFSET 48

const byte numChars = 32;
char receivedChars[numChars]; // an array to store the received data

boolean newData = false;
int INA = 2;
int INB = 3;
int INC = 4;
int IND = 5;
int INE = 6;
int INF = 7;
int ING = 8;
int INH = 9;

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
  digitalWrite(INE, HIGH);
  digitalWrite(INF, HIGH);
  digitalWrite(ING, HIGH);
  digitalWrite(INH, HIGH);
  
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
  char* binary = "";
  char* temp;
  int bit;
  
  if (newData == true) {
    Serial.println(receivedChars);
    
    //receive hexadecimal number only. eg x4F
    if( (strlen(receivedChars) != 2) ){//|| (receivedChars[0] != 'x') ){
      Serial.println("String command not recognized");
      newData = false;
      return;
    }
    
    if( (htob(receivedChars[0]) == ERROR) || (htob(receivedChars[1]) == ERROR) ){
      Serial.println("Not a hexadecimal");
      newData = false;
      return;
    }

    for(int i=0; i<=1; i++){
      binary=htob(receivedChars[i]);
      for(int j=9; j>=6; j--){
        bit = binary[9-j]-OFFSET;
        digitalWrite((j-i*4), 1-bit);
        Serial.print(bit);
      }
    }
    Serial.println();

    newData = false;
  }
}

const char * htob(unsigned char c)
{
  const char* quads[] = {"0000", "0001", "0010", "0011", "0100", "0101",
                     "0110", "0111", "1000", "1001", "1010", "1011",
                     "1100", "1101", "1110", "1111"};

  if (c >= '0' && c <= '9') return quads[     c - '0'];
  if (c >= 'A' && c <= 'F') return quads[10 + c - 'A'];
  if (c >= 'a' && c <= 'f') return quads[10 + c - 'a'];
  return ERROR;
}
