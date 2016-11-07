# ===========================================
#
# Filename: robot.py
#
# Description: 
#
# Contains the robot class
#
# ===========================================
import serial
from time import sleep
import math
import numpy as np
import random

GEAR = {1: [80, 100],
        2: [100, 120],
        3: [120, 148],
        4: [140, 168],
        5: [160, 190],
        6: [180, 208],
        7: [200, 230]}

BREAK = {1: [100, 110],
         2: [100, 120],
         3: [120, 140],
         4: [140, 160],
         5: [160, 190],
         6: [180, 208],
         7: [200, 230]}

TURN_SPEED = {1: 53.57,
              2: 111.57}

class Robot(object):
    

    # === FUNCTION ==============================
    # 
    # Description:
    #
    # Initialize the robot
    #
    # ===========================================
    def __init__(self):

        self.port = '/dev/ttyACM0'
        self.serialRead = serial.Serial(self.port, 9600, timeout=1)
       
        # Wait if serial port is not open yet
        while not self.serialRead.isOpen():
            sleep(1)

        print("Waiting for serial port connection ...")
        sleep(2)

        print("Running ...")



    # === ROBOT CONTROL ========================
    # 
    # Description:
    #
    # Functions to control robot only used inside
    # inside this file.
    #
    # ===========================================
    def send_command(self, cmd):
        """Sends a command to the Arduino robot controller"""
        self.serialRead.write(cmd.encode('ascii'))
        str_val=self.serialRead.readline()
        return str_val
    
    def stop(self):
        """Send a stop command to stop motors"""
        cmd='s\n'
        return self.send_command(cmd)
    
    def go_diff(self, speedLeft, speedRight, dirLeft, dirRight):
        """Start left motor with speed speedLeft (in [0;255]) and direction dirLeft (0=reverse, 1=forward)
           and right motor with speed speedRight (in [0;255]) and direction dirRight (0=reverse, 1=forward)"""
        cmd = 'd' + str(speedLeft) + ',' + str(speedRight) + ',' + str(dirLeft) + ',' + str(dirRight) + '\n'
        return self.send_command(cmd)


    # === ROBOT MOVEMENT ========================
    # 
    # Description:
    #
    # Functions to move the robot
    #
    # ===========================================
    def turn_break(self, direction):


        if direction == 'right':
            self.go_diff(GEAR[1][0] + 18, GEAR[1][1] + 13, 0, 1)
            sleep(0.03)
        else:
            self.go_diff(GEAR[1][0] + 20, GEAR[1][1] + 30, 1, 0)
            sleep(0.03)

    def turn(self, degrees, direction):
    

        if degrees <= 22.5:
            sleep_time = np.divide(degrees, TURN_SPEED[1])
        else:
            sleep_time = np.divide(22.5, TURN_SPEED[1])
            sleep_time += np.divide((degrees - 22.5), TURN_SPEED[2])
            
        if direction == 'right':
            self.go_diff(GEAR[1][0] + 20, GEAR[1][1] + 15, 1, 0)
        else:
            self.go_diff(GEAR[1][0] + 10, GEAR[1][1] + 10, 0, 1)

        if 0 < sleep_time:
            sleep(sleep_time)

        self.turn_break(direction)
        self.stop()

