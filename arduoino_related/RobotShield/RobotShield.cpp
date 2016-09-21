/*
  RobotShield.cpp - Library for arduino Robot Shield
  Created by Jonathan Luke, RobotBits.co.uk
  Version 1.0, 22 April 2011
  
  Version 1.1, 2 December 2011
  Added go, go_back, go_cw, go_ccw
    
  Version 1.2, 21 January 2012
  Updated to support Arduino 1.0 software

  Version 1.3, 29 August 2013
  Added "stop" to each step command
  
  Released into the public domain.
 
  Version 1.4, August 2016
  added go_diff command
*/

#include "RobotShield.h"

// define the pins used by the robot shield
int speedA = 6;          // pin 6 sets the speed of motor A (this is a PWM output)
int speedB = 9;          // pin 9 sets the speed of motor B (this is a PWM output) 
int dirA = 8;            // pin 8 sets the direction of motor A
int dirB = 7;            // pin 7 sets the direction of motor B


// define the direction of motor rotation - this allows you change the  direction without effecting the hardware
int fwdA  =  HIGH;       // this sketch assumes that motor A is the right-hand motor of your robot (looking from the back of your robot)
int revA  =  LOW;        // (note this should ALWAYS be opposite the fwdA)
int fwdB  =  HIGH;        
int revB  =  LOW;        // (note this should ALWAYS be opposite the fwdB)


// define the variables used by the RobotShield
int dist;
int angle;
int vel;

//values for stopwatch
unsigned long start_time = 0;
unsigned long stop_time = 0;
unsigned long time_diff = 0;

RobotShield::RobotShield()                           // sets up the pinModes for the pins we are using
{
  pinMode (dirA, OUTPUT);         
  pinMode (dirB, OUTPUT); 
  pinMode (speedA, OUTPUT); 
  pinMode (speedB, OUTPUT); 
}


void RobotShield::stop()                            // stop: force both motor speeds to 0 (low)
{                              
 digitalWrite (speedA, LOW); 
 digitalWrite (speedB, LOW);
}

             
void RobotShield::forward(int dist, int vel)       // forward: both motors set to forward direction
{
  digitalWrite (dirA, fwdA); 
  digitalWrite (dirB, fwdB);
  analogWrite (speedA, vel);                        // both motors set to same speed
  analogWrite (speedB, vel); 
  delay (dist);                                     // wait for a while (dist in mSeconds)
  
  digitalWrite (speedA, LOW); 						// stop motors 
  digitalWrite (speedB, LOW);
 }
             
             
void RobotShield::reverse(int dist, int vel)       // reverse: both motors set to reverse direction
{
  digitalWrite (dirA, revA); 
  digitalWrite (dirB, revB);
  analogWrite (speedA, vel);                        // both motors set to same speed
  analogWrite (speedB, vel); 
  delay (dist);  									// wait for a while (dist in mSeconds)
  
  digitalWrite (speedA, LOW); 						// stop motors
  digitalWrite (speedB, LOW);                                                 
}    


void RobotShield::rot_cw (int angle, int vel)      // rotate clock-wise: right-hand motor reversed, left-hand motor forward
{
  digitalWrite (dirA, revA); 
  digitalWrite (dirB, fwdB);
  analogWrite (speedA, vel);                        // both motors set to same speed
  analogWrite (speedB, vel); 
  delay (angle);                                    // wait for a while (angle in mSeconds)      
  
  digitalWrite (speedA, LOW); 						// stop motors
  digitalWrite (speedB, LOW);        
}
             
             
void RobotShield::rot_ccw (int angle, int vel)     // rotate counter-clock-wise: right-hand motor forward, left-hand motor reversed
{        
  digitalWrite (dirA, fwdA); 
  digitalWrite (dirB, revB);
  analogWrite (speedA, vel);                        // both motors set to same speed
  analogWrite (speedB, vel); 
  delay (angle);                                    // wait for a while (angle in mSeconds)        
  
  digitalWrite (speedA, LOW); 						// stop motors
  digitalWrite (speedB, LOW);      
}
             
             
void RobotShield::turn_right (int angle, int vel)  // turn right: right-hand motor stopped, left-hand motor forward
{
  digitalWrite (dirA, revA); 
  digitalWrite (dirB, fwdB);
  digitalWrite (speedA, LOW);                       // right-hand motor speed set to zero
  analogWrite (speedB, vel); 
  delay (angle);                                    // wait for a while (angle in mSeconds)   
  
  digitalWrite (speedA, LOW); 						// stop motors
  digitalWrite (speedB, LOW);           
}
             
             
void RobotShield::turn_left (int angle, int vel)   // turn left: left-hand motor stopped, right-hand motor forward
{
  digitalWrite (dirA, fwdA); 
  digitalWrite (dirB, revB);
  analogWrite (speedA, vel);
  digitalWrite (speedB, LOW);                       // left-hand motor speed set to zero
  delay (angle);                                    // wait for a while (angle in mSeconds)       
  
  digitalWrite (speedA, LOW); 						// stop motors
  digitalWrite (speedB, LOW);       
}

void RobotShield::go(int vel) 						// forward: both motors set to forward direction
{          
  digitalWrite (dirA, fwdA); 
  digitalWrite (dirB, fwdB);
  analogWrite (speedA, vel);   				// both motors set to same speed
  analogWrite (speedB, vel); 
}
             
void RobotShield::go_back(int vel)           // reverse: both motors set to reverse direction
{
  digitalWrite (dirA, revA); 
  digitalWrite (dirB, revB);
  analogWrite (speedA, vel);   				// both motors set to same speed
  analogWrite (speedB, vel);              
}
             
void RobotShield::go_cw (int vel)          // rotate clock-wise: right-hand motor reversed, left-hand motor forward
{
  digitalWrite (dirA, revA); 
  digitalWrite (dirB, fwdB);
  analogWrite (speedA, vel);   				// both motors set to same speed
  analogWrite (speedB, vel);           
}
             
void RobotShield::go_ccw (int vel)         // rotate counter-clock-wise: right-hand motor forward, left-hand motor reversed
{
  digitalWrite (dirA, fwdA); 
  digitalWrite (dirB, revB);
  analogWrite (speedA, vel);   				// both motors set to same speed
  analogWrite (speedB, vel);             
}


void RobotShield::go_diff(int velLeft, int velRight, int dirLeft, int dirRight)
{
    digitalWrite (dirA, dirRight);
    digitalWrite (dirB, dirLeft);
    analogWrite (speedA, velRight);
    analogWrite (speedB, velLeft);
}


int RobotShield::stop_watch(int start_or_stop)      // stopwatch
{
    if(start_or_stop == 1){
        start_time = millis();
        return start_time;
    } else{
        stop_time = millis();
        time_diff = stop_time - start_time;
        start_time = 0;
        stop_time = 0;
        return time_diff;
    }
}