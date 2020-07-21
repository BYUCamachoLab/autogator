import atexit
import keyboard
import numpy as np
import time
import thorlabs_kinesis as tk
from thorlabs_kinesis import kcube_dcservo as kcdc
from autogator.models.stage import Z825B, VariableRotationalMotor
import enum

from ctypes import (
    c_char_p,
    c_int,
    c_short,
    c_char,
    POINTER,
    cdll,
    byref
)        

from thorlabs_kinesis._utils import (
    bind
)

lib = cdll.LoadLibrary("Thorlabs.MotionControl.KCube.DCServo.dll")

lateral_mot = c_char_p(bytes("27504851", "utf-8"))
longitudinal_mot = c_char_p(bytes("27003497", "utf-8"))
motors = [lateral_mot, longitudinal_mot]

def open_motors():
    global motors
    for serialno in motors:
        kcdc.CC_Open(serialno)
        kcdc.CC_StartPolling(serialno, c_int(20))
        kcdc.CC_ClearMessageQueue(serialno)
    
    time.sleep(3)

    for serialno in motors:
        homeable = bool(kcdc.CC_CanHome(serialno))
        print("Can home:", homeable)
        #Get Motor Position
        accel_param, vel_param = c_int(), c_int()
        kcdc.CC_GetJogVelParams(serialno, byref(accel_param), byref(vel_param))
        print("Acceleration:", accel_param.value, "Velocity:", vel_param.value)
        kcdc.CC_RequestPosition(lateral_mot)
        kcdc.CC_RequestPosition(longitudinal_mot)
        current_motor_pos = kcdc.CC_GetPosition(serialno)
        print("Position:", current_motor_pos)

@atexit.register
def close_motors():
    global motors
    for serialno in motors:
        kcdc.CC_StopPolling(serialno)
        kcdc.CC_Close(serialno)

open_motors()

# Get velocity params
# Set velocity params

while True:
    if keyboard.is_pressed('left arrow'):
        kcdc.CC_MoveAtVelocity(lateral_mot, kcdc.MOT_TravelDirection.MOT_Reverse.value)
        pass
    elif keyboard.is_pressed('right arrow'):
        kcdc.CC_MoveAtVelocity(lateral_mot, kcdc.MOT_TravelDirection.MOT_Forwards.value)
        pass
    if keyboard.is_pressed('up arrow'):
        kcdc.CC_MoveAtVelocity(longitudinal_mot, kcdc.MOT_TravelDirection.MOT_Forwards.value)
    elif keyboard.is_pressed('down arrow'):
        kcdc.CC_MoveAtVelocity(longitudinal_mot, kcdc.MOT_TravelDirection.MOT_Reverse.value)