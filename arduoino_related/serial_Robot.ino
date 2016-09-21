//  serial_Robot     version 1.0      J.Luke     30/08/2013
//                   version 1.1      Kim Steenstrup Pedersen, DIKU, August 2016
//
//  This sketch converts an Arduino with a RobotShield into a serial robot controller.
//
//  The sketch provides basic motion control as well as access to Arduinos analog inputs over the
//  serial or USB port for robotics applications. The simple commands mean the controller can be
//  interfaced to anything with a serial or USB port including a PC, Raspberry Pi, microcontroller 
//  or another Arduino.
//
//  This sketch uses the RobotShield library which can be downloaded from www.frindo.com and provides
//  a mix of stepped commands, continuous commands and analog measurements. The movement of your robot 
//  is controlled by sending a single character command over the serial port.
//  
//  Stepped commands make your robot move in a specific way for a fixed period of time. The length of time
//  is set using the "step_time" and "turn_time" variables. All times are in mS (milliseconds).
//
//    f = Forward, b = Backwards, l = rotate Left, r = rotate Right 
//
//  Continuous commands make you robot move in the same way continuously until you send a stop or other command.  
//
//    s = Stop, g = Go, v = Reverse, n = rotate Left, m = rotate Right 
//
//  The speed of the motors during all movements is set by the "motor_speed" and "turn_speed". Motor speeds 
//  range from 0 to 255; where 0 = 0% of full speed and 255 = 100% of full speed. 
//
//  Set the motor_speed and turn_speed with these commands followed by a byte representing the wanted speed.
//
//    z = motor_speed , x = turn_speed
//
//  Set the step_time used by f and b and the turn_time used by l and r followed by an int representing the wanted time in miliseconds:
//
//    t = step_time, y = turn_time
//
//  Start motors with different speeds and directions
//
//    d = Go differential
//
//  followed by 4 integers separated by commas: velLeft (a byte [0:255]), velRight (a byte [0:255]), dirLeft (0 = reverse and 1 = forward) 
//  and dirRight (0 = reverse and 1 = forward). Example:
// 
//    d128,200,1,0
//
//  c = start/stop stopwatch in milliseconds
//
//  Analog measurements are requested by sending a single numeric character over the serial port, the character 
//  from 0 to 5 represents the Arduino port number. The Arduino makes an analog measurement (0 to 5 volts) and 
//  returns a digital value (0 to 1023) where 0 = 0 volts and 1023 = 5 volts.
//
//    0 = A0, 1 = A1, 2 = A2, 3 = A3, 4 = A4, 5 = A5
//
//  For support or suggestions, please use the forums at www.frindo.com
//
//  This code is open source so share, change, improve and contribute to the robot building community!


#include <RobotShield.h> // include the RobotShield library

RobotShield rs;          // create an instance of the RobotShield class called "rs"

// define variables used
int Response;
int motor_speed = 128;
int turn_speed = 128;
int step_time = 1000; //mS
int turn_time = 250; //mS

void setup() {       
              
    Serial.begin(9600);             // set up serial port
}     
            
void loop() { 
 
    if (Serial.available() > 0)            // if something has been received 
      {
        int incoming = Serial.read();      // go read it
        
        if ((char)incoming == 'f')
        {
          rs.forward(step_time, motor_speed);
          Serial.println("Forward");
        }
        
        else if ((char)incoming == 'b')
        {
          rs.reverse(step_time, motor_speed); 
          Serial.println("Back");
        }
        
        else if ((char)incoming == 'l')
        {
          rs.rot_ccw(turn_time, turn_speed); 
          Serial.println("Left");
        }
        
        else if ((char)incoming == 'r')
        {
          rs.rot_cw(turn_time, turn_speed); 
          Serial.println("Right");
        }
        
        else if ((char)incoming == 's')
        {
          rs.stop(); 
          Serial.println("Stop");
        }
        
        else if ((char)incoming == 'g')
        {
          rs.go(motor_speed); 
          Serial.println("Go");
        }
        
        else if ((char)incoming == 'v')
        {
          rs.go_back(motor_speed); 
          Serial.println("Reverse");
        }
        
        else if ((char)incoming == 'm')
        {
          rs.go_cw(turn_speed); 
          Serial.println("Clockwise");
        }
        
        else if ((char)incoming == 'n')
        {
          rs.go_ccw(turn_speed); 
          Serial.println("Counter Clockwise");
        }
        
        else if ((char)incoming == '0')
        {
          Response = analogRead(0);
          Serial.println(Response); 
        }

        else if ((char)incoming == '1')
        {
          Response = analogRead(1);
          Serial.println(Response); 
        }
        
        else if ((char)incoming == '2')
        {
          Response = analogRead(2);
          Serial.println(Response); 
        }
        
        else if ((char)incoming == '3')
        {
          Response = analogRead(3);
          Serial.println(Response); 
        }
        
        else if ((char)incoming == '4')
        {
          Response = analogRead(4);
          Serial.println(Response); 
        }
        
        else if ((char)incoming == '5')
        {
          Response = analogRead(5);
          Serial.println(Response); 
        }

        else if ((char)incoming == 'z')
        {
          String inString = "";
          char inChars[3];
          Serial.readBytesUntil('\n', inChars, 3);
          for (int i=0; i < 4; i++) { 
            if (isDigit(inChars[i])) {
              inString += (char)inChars[i];
            }
          }
          motor_speed = inString.toInt();
          Serial.print("Setting motor speed to ");
          Serial.println(motor_speed);
        }
  
        else if ((char)incoming == 'x')
        {          
          String inString = "";
          char inChars[3];
          Serial.readBytesUntil('\n', inChars, 3);
          for (int i=0; i < 4; i++) { 
            if (isDigit(inChars[i])) {
              inString += (char)inChars[i];
            }
          }
          turn_speed = inString.toInt();
          Serial.print("Setting turn speed to ");
          Serial.println(turn_speed);
        }
        
        else if ((char)incoming == 't')
        {
          String inString = "";
          int len = 5;
          char inChars[len];
          Serial.readBytesUntil('\n', inChars, len);
          for (int i=0; i < len; i++) { 
            if (isDigit(inChars[i])) {
              inString += (char)inChars[i];
            }
          }
          step_time = inString.toInt();
          Serial.print("Setting step_time to ");
          Serial.println(step_time);
        }
        
        else if ((char)incoming == 'y')
        {
          String inString = "";
          int len = 5;
          char inChars[len];
          Serial.readBytesUntil('\n', inChars, len);
          for (int i=0; i < len; i++) { 
            if (isDigit(inChars[i])) {
              inString += (char)inChars[i];
            }
          }
          turn_time = inString.toInt();
          Serial.print("Setting turn_time to ");
          Serial.println(turn_time);
        }
        
        else if ((char)incoming == 'd')
        {
          int params[4];
          int idx = 0;
          String inString = "";
          
          int len = 11;
          char inChars[len];
          Serial.readBytesUntil('\n', inChars, len);
          for (int i=0; i < len; i++) { 
            if (isDigit(inChars[i])) {
              inString += (char)inChars[i];
            } else if (inChars[i] ==',') {
              params[idx] = inString.toInt();
              inString = "";
              idx++;
            }
          }
          
          params[idx] = inString.toInt();
          idx++;
                    
          if (idx == 4) {
            int dirLeft = HIGH;
            if (params[2] == 0)
                dirLeft = LOW;
            int dirRight = HIGH;
            if (params[3] == 0)
                dirRight = LOW;
            rs.go_diff(params[0], params[1], dirLeft, dirRight);
            Serial.print("Go diff ");
            Serial.print(params[0]);
            Serial.print(",");
            Serial.print(params[1]);
            Serial.print(",");
            Serial.print(params[2]);
            Serial.print(",");
            Serial.println(params[3]);
          } else {
            Serial.println("ERROR");
          }
        }
        else if ((char)incoming == 'c')
        {
          int param[1];
          String inString = "";
          int len = 1;
          char inChars[len];
          Serial.readBytesUntil('\n', inChars, len);
          inString += inChars[0];
          int z = inString.toInt();
          int x = rs.stop_watch(z);
          Serial.print(x);
        }
    }        
}
