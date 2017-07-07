#include <string.h>

#define ERROR -1
#define OFFSET 48
#define HEXCHAR 3
#define HIGHESTPIN 9
#define PIN_D2 2
#define PIN_D3 3
#define PIN_D4 4
#define PIN_D5 5
#define PIN_D6 6
#define PIN_D7 7
#define PIN_D8 8
#define PIN_D9 9

const byte NumChars = 32;
char ReceivedChars[NumChars]; // an array to store the received data
boolean NewData = false;

//--------------------------------------------------------------------------------------------------
/**
 * Initializes pins D2 to D9 as outputs and set them off. Baud rate set to 115200
 *
 */
//--------------------------------------------------------------------------------------------------
void setup() {
  //set pins D2 to D9 to be outputs
  pinMode(PIN_D2 , OUTPUT);
  pinMode(PIN_D3 , OUTPUT);
  pinMode(PIN_D4 , OUTPUT);
  pinMode(PIN_D5 , OUTPUT);
  pinMode(PIN_D6 , OUTPUT);
  pinMode(PIN_D7 , OUTPUT);
  pinMode(PIN_D8 , OUTPUT);
  pinMode(PIN_D9 , OUTPUT);

  //initialize relays to be normally off. HIGH = off
  digitalWrite(PIN_D2, HIGH);
  digitalWrite(PIN_D3, HIGH);
  digitalWrite(PIN_D4, HIGH);
  digitalWrite(PIN_D5, HIGH);
  digitalWrite(PIN_D6, HIGH);
  digitalWrite(PIN_D7, HIGH);
  digitalWrite(PIN_D8, HIGH);
  digitalWrite(PIN_D9, HIGH);

  Serial.begin(115200);
}

//--------------------------------------------------------------------------------------------------
/**
 * infinite loop main function to check for any data on serial monitor to read
 *
 */
//--------------------------------------------------------------------------------------------------
void loop() {
  recvWithEndMarker();
  showNewData();
}

//--------------------------------------------------------------------------------------------------
/**
 * Receives a string of data from serial port monitor if any
 *
 * @return
 *      NewData = true if there is input data from serial port monitor
 *      String of characters in ReceivedChars[] array
 */
//--------------------------------------------------------------------------------------------------
void recvWithEndMarker() {
  static byte ndx = 0;
  char endMarker = '\n';
  char rc;

  while (Serial.available() > 0 && NewData == false) {
    rc = Serial.read();

    if (rc != endMarker) {
      ReceivedChars[ndx] = rc;
      ndx++;
      if (ndx >= NumChars) {
        ndx = NumChars - 1;
      }
    }
    else {
      ReceivedChars[ndx] = '\0'; // terminate the string
      ndx = 0;
      NewData = true;
    }
  }
}

//--------------------------------------------------------------------------------------------------
/**
 * Displays data on to serial monitor and test if input is 1 byte in hex form. For example, valid
 * entries are x0F, x00, xE5
 * The first hexadecimal will determine the Gpio pins D2, D3, D4 and D5 and the corresponding state
 * on the relay.
 *
 * @return
 *      Error if not in the right form. Otherwise, output of 1 state of the 4 relay module.
 *      For example, x05 will turn D2 and D4 on (which turns IN1 and IN3 on) which
 *      represents 00000101 in bits
 */
//--------------------------------------------------------------------------------------------------
void showNewData() {
  char* binary = "";
  int bit;

  if (NewData == true) {
    Serial.println(ReceivedChars);

    //receive hexadecimal number only. eg x4F
    if( (strlen(ReceivedChars) != HEXCHAR) ){
      Serial.println("String command not recognized");
      NewData = false;
      return;
    }

    if( ReceivedChars[0] != 'x' || ( hextobin(ReceivedChars[1]) == ERROR ) || ( hextobin(ReceivedChars[2])  == ERROR ) ){
      Serial.println("Not a hexadecimal");
      NewData = false;
      return;
    }

    for( int i = 0; i <= 1; i++ ){
      binary = hextobin(ReceivedChars[i+1]);
      for( int j = HIGHESTPIN; j > HIGHESTPIN-4; j--){
        bit = binary[HIGHESTPIN-j] - OFFSET;
        digitalWrite((j - i * 4), !bit);
        Serial.print(bit);
      }
    }
    Serial.println();

    NewData = false;
  }
}

//--------------------------------------------------------------------------------------------------
/**
 * Function to change hex value to 4 bit binary, else ERROR.
 *
 * @return
 *      4 bit binary
 */
//--------------------------------------------------------------------------------------------------
const char * hextobin(unsigned char c)
{
  const char* quads[] = {"0000", "0001", "0010", "0011", "0100", "0101",
                     "0110", "0111", "1000", "1001", "1010", "1011",
                     "1100", "1101", "1110", "1111"};

  if (c >= '0' && c <= '9') return quads[     c - '0'];
  if (c >= 'A' && c <= 'F') return quads[10 + c - 'A'];
  if (c >= 'a' && c <= 'f') return quads[10 + c - 'a'];
  return ERROR;
}

