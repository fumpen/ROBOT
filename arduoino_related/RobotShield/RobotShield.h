/*
  RobotShield.h - Library for arduino Robot Shield
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

#ifndef RobotShield_h
#define RobotShield_h


#if defined(ARDUINO) && ARDUINO >= 100
  #include "Arduino.h"
#else
  #include "WProgram.h"
#endif


class RobotShield
{
  public:
    RobotShield();
    void stop();
    void forward(int dist, int vel);
    void reverse(int dist, int vel);
    void rot_cw(int dist, int vel);
    void rot_ccw(int dist, int vel);  
    void turn_right(int dist, int vel);
    void turn_left(int dist, int vel);

// new in Version 1.1 2 December 2011    
    void go(int vel);
    void go_back(int vel);
    void go_cw(int vel);
    void go_ccw(int vel);
    
    
// Added by Kim Steenstrup Pedersen, DIKU, August 2016
    
    /**
     * Set left motor speed to velLeft and direction to dirLeft (can be either LOW for 
     * reverse or HIGH for forward) and the right motor speed to velRight and direction to dirRight
     */
    void go_diff(int velLeft, int velRight, int dirLeft, int dirRight);


// Added by desperate participants of robot-course
    int stop_watch(int start_or_stop);
};

#endif