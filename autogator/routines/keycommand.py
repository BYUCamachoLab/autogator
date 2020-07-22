import os
os.environ['PATH'] = "C:\\Program Files\\ThorLabs\\Kinesis" + ";" + os.environ['PATH']
import atexit
import keyboard
import numpy as np
import time
import thorlabs_kinesis as tk
from thorlabs_kinesis import kcube_dcservo as kcdc
from autogator.models.stage import Z825B, VariableRotationalMotor

from ctypes import (
    c_char_p,
    c_int,
    c_short,
    c_char,
    POINTER,
    byref,
    create_string_buffer,
)  

from ctypes.wintypes import (
    DWORD,
    WORD,
)

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

def block(serialno):
    message_type, message_id, message_data = WORD(), WORD(), DWORD()
    kcdc.CC_WaitForMessage(serialno, byref(message_type), byref(message_id), byref(message_data))
    while (int(message_type.value) != 2) or (int(message_id.value) != 1):
        kcdc.CC_WaitForMessage(serialno, byref(message_type), byref(message_id), byref(message_data))

if kcdc.TLI_BuildDeviceList() == 0:
    print("Device list built (no errors).")

    size = kcdc.TLI_GetDeviceListSize()
    print(size, "device(s) found.")

    serialnos = create_string_buffer(100)
    kcdc.TLI_GetDeviceListByTypeExt(serialnos, 100, 27)
    serialnos = list(filter(None, serialnos.value.decode("utf-8").split(',')))
    print("Serial #'s:", serialnos)

    open_motors()

    acceleration_param = c_int()
    velocity_param = c_int()

    # Get velocity params
    kcdc.CC_GetVelParams(lateral_mot, byref(acceleration_param), byref(velocity_param))
    print(acceleration_param.value, velocity_param.value)
    kcdc.CC_GetVelParams(longitudinal_mot, byref(acceleration_param), byref(velocity_param))
    print(acceleration_param.value, velocity_param.value)

    # Set velocity params
    # kcdc.CC_SetVelParams(lateral_mot, acceleration_param, velocity_param)
    # kcdc.CC_SetVelParams(longitudinal_mot, acceleration_param, velocity_param)

    input('Press <ENTER> to active motion...')

    while True:
        if keyboard.is_pressed('left arrow'):
            kcdc.CC_MoveAtVelocity(lateral_mot, kcdc.MOT_TravelDirection.MOT_Reverse.value)
            # We may actually not want to block, so that we can detect other keyboard
            # commands such as one to STOP the motion
            block(lateral_mot)
            # If we don't block, then what we should do is monitor for a keypress lift event,
            # and use CC_StopProfiled (for CC_MoveAtVelocity, not for jogging) in that case.
            # We may also want an "Emergency Stop All" button, perhaps the spacebar, that
            # uses CC_StopImmediate and stops the motion of all stages.
        elif keyboard.is_pressed('right arrow'):
            kcdc.CC_MoveAtVelocity(lateral_mot, kcdc.MOT_TravelDirection.MOT_Forwards.value)
            block(lateral_mot)
        if keyboard.is_pressed('up arrow'):
            kcdc.CC_MoveAtVelocity(longitudinal_mot, kcdc.MOT_TravelDirection.MOT_Forwards.value)
            block(longitudinal_mot)
        elif keyboard.is_pressed('down arrow'):
            kcdc.CC_MoveAtVelocity(longitudinal_mot, kcdc.MOT_TravelDirection.MOT_Reverse.value)
            block(longitudinal_mot) 