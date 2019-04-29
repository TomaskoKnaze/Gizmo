// Bluetooth Communication

#include <SoftwareSerial.h>
SoftwareSerial bt (0,5);

const byte buffSize = 40;
char inputBuffer[buffSize];
const char startMarker = '<';
const char endMarker = '>';
byte bytesRecvd = 0;
boolean readInProgress = false;
boolean newDataFromPC = false;
char messageFromPC[buffSize] = {0};

//----------------------------------




// Sensors 
#define sensor1 A3 
#define sensor2 A4 
#define sensor3 A5 

const int TOUCH_BUTTON_PIN = 3;  // Input pin for touch state
int touch_buttonState = 0;

//----------------------------------



// Motor Driver
#include "DualTB9051FTGMotorShield.h"
DualTB9051FTGMotorShield md;
//-----------------------------------



int roam = 0;
int caught = 0;
int button = 0;




void setup() {
  bt.begin(9600); // start the serial port
  bt.println("<Arduino is ready>");
  
  pinMode(8, OUTPUT);
  digitalWrite(8, HIGH);
  
  pinMode(TOUCH_BUTTON_PIN, INPUT);

  md.init();
  md.enableDrivers();
  
  pinMode(4, INPUT);
  digitalWrite(4, HIGH); 

}

void loop() {
  getDataFromPC();
  caught = am_i_caught();
  button = is_button_pressed();
  replyToPC();
  driving(roam);
  

}



//Next 3 Functions originally from user Robin2, modified--------------------
//http://forum.arduino.cc/index.php?topic=225329.msg1810764#msg1810764

void getDataFromPC() {

    // receive data from PC and save it into inputBuffer
    
  if(bt.available() > 0) {

    char x = bt.read();
      
    if (x == endMarker) {
      readInProgress = false;
      newDataFromPC = true;
      inputBuffer[bytesRecvd] = 0;
      parseData();
    }
    
    if(readInProgress) {
      inputBuffer[bytesRecvd] = x;
      bytesRecvd ++;
      if (bytesRecvd == buffSize) {
        bytesRecvd = buffSize - 1;
      }
    }

    if (x == startMarker) { 
      bytesRecvd = 0; 
      readInProgress = true;
    }
  }
}



void parseData() {

    // split the data into its parts
    
  char * strtokIndx; // this is used by strtok() as an index
  
  strtokIndx = strtok(inputBuffer,",");      // get the first part - the string
  strcpy(messageFromPC, strtokIndx); // copy it to messageFromPC
  
  strtokIndx = strtok(NULL, ","); // this continues where the previous call left off
  roam = atoi(strtokIndx);     // convert this part to an integer
       

}

void replyToPC() {

  if (newDataFromPC) {
    newDataFromPC = false;
    bt.print("<Caught: ");
    bt.print(caught);
    bt.print(", cbuttonpress: ");
    bt.print(button);
    bt.println(">");
  }
}
//-------------------------------


int speed_calc(int distance){
  int motor_speed = (200/30)*distance;
  return motor_speed;
}

int distance_calc(int sensor_value){
  sensor_value = 0.0010 * sensor_value;
  int distance = 13*pow(sensor_value, -1);
  return distance;
}

int am_i_caught(){
  int im_caught = 0;
  touch_buttonState = digitalRead(TOUCH_BUTTON_PIN);
  if (touch_buttonState == HIGH) {
    im_caught = 1;
  } else {
    im_caught = 0;
  }
  return im_caught;
}

int is_button_pressed(){
  int button_pressed = 0;
  button_pressed = digitalRead(4);
  return button_pressed;
}

void driving(int should_i_be_driving){
  if (should_i_be_driving == 1){
    delay(1);

    int distance1 = distance_calc(analogRead(sensor1));
    int distance2 = distance_calc(analogRead(sensor2));
    int distance3 = distance_calc(analogRead(sensor3));

    if (distance1 <= 30){
      md.setM2Speed(speed_calc(distance1));
      delay(2);
    }

    if (distance2 <= 30){
      md.setM1Speed(speed_calc(distance2));
      delay(2);
    }

    if (distance3 <= 30){
      md.setM1Speed(speed_calc(-distance3));
      delay(2);
    }
  }
}

