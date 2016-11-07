# ===========================================
#
# Filename: robot.py
#
# Description: 
#
# Contains the robot object.
#
# ===========================================

from time import sleep
import serial

class Robot(object):
    """Defines the Frindo robot API""" 
    def __init__(self):
        self.port = '/dev/ttyACM0'

        self.serialRead = serial.Serial(self.port,9600, timeout=1)

        # Wait if serial port is not open yet
        while not self.serialRead.isOpen():
            sleep(1)

        print("Waiting for serial port connection ...")
        sleep(2)

        print("Running ...")
        
        
    def send_command(self, cmd):
        """Sends a command to the Arduino robot controller"""
        self.serialRead.write(cmd.encode('ascii'))
        str_val=self.serialRead.readline()
        return str_val


    # === ROBOT MOVEMENT ========================
    # ===========================================
        
         
    def stop(self):
        """Send a stop command to stop motors"""
        cmd='s\n'
        return self.send_command(cmd)
        
    def go_diff(self, speedLeft, speedRight, dirLeft, dirRight):
        """Start left motor with speed speedLeft (in [0;255]) and direction dirLeft (0=reverse, 1=forward)
           and right motor with speed speedRight (in [0;255]) and direction dirRight (0=reverse, 1=forward)"""
        cmd = 'd' + str(speedLeft) + ',' + str(speedRight) + ',' + str(dirLeft) + ',' + str(dirRight) + '\n'
        return self.send_command(cmd)
    
    # === ROBOT SENSOR ==========================
    # read_ir_sensor:
    #
    #     Send a read command with sensorid and
    #     and return sensor value. Return -1 if
    #     error occurs.
    #
    #  read_*_ir_sensor:
    # 
    #     Read sensor and return the measured
    #     voltage in range [0; 1023].
    #     (From 0 to 5 volts)
    #
    # ===========================================
    
    def read_ir_sensor(self, sensorid):
        cmd=str(sensorid) + '\n'
        str_val=self.send_command(cmd)
        if len(str_val) > 0:
            return int(str_val)
        else:
            return -1
            
    def read_front_ir_sensor(self):
        return self.read_ir_sensor(0)
        
    def read_right_ir_sensor(self):
        return self.read_ir_sensor(1)
        
    def read_left_ir_sensor(self):
        return self.read_ir_sensor(2)
         

