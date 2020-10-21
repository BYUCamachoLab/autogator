import os
os.environ['PATH'] = "C:\\Program Files\\ThorLabs\\Kinesis" + ";" + os.environ['PATH']

import atexit
import time
from enum import Enum, auto

import keyboard
import numpy as np
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

class MoveMode(Enum):
    JOG = auto()
    CONTINUOUS = auto()

STEPS_PER_MM = 34304
STEP_SIZE_MM = 0.001

def mm_to_steps(mm):
    return round(mm * STEPS_PER_MM)

def steps_to_mm(steps):
    return steps / STEPS_PER_MM

move_mode = MoveMode.JOG
lateral_mot = c_char_p(bytes("27504851", "utf-8"))
longitudinal_mot = c_char_p(bytes("27003497", "utf-8"))
motors = [lateral_mot, longitudinal_mot]

lat_moving = False
long_moving = False
rot_moving = False

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

def move_left(e):
    global move_mode, lateral_mot, lat_moving
    if move_mode == MoveMode.JOG:
        kcdc.CC_MoveJog(lateral_mot, kcdc.MOT_Forwards)
        lat_moving = True
    if move_mode == MoveMode.CONTINUOUS and lat_moving == False:
        kcdc.CC_MoveAtVelocity(lateral_mot, kcdc.MOT_Forwards)
        lat_moving = True
        # kcdc.CC_MoveAtVelocity(lateral_mot, kcdc.MOT_TravelDirection.MOT_Reverse.value)

def release_left(e):
    global move_mode, lateral_mot, lat_moving
    if move_mode == MoveMode.CONTINUOUS:
        kcdc.CC_StopProfiled(lateral_mot)
    lat_moving = False
        # If we don't block, then what we should do is monitor for a keypress lift event,
        # and use CC_StopProfiled (for CC_MoveAtVelocity, not for jogging) in that case.

def move_right(e):
    global move_mode, lateral_mot, lat_moving
    if move_mode == MoveMode.JOG:
        kcdc.CC_MoveJog(lateral_mot, kcdc.MOT_Reverse)
        lat_moving = True
    if move_mode == MoveMode.CONTINUOUS and lat_moving == False:
        kcdc.CC_MoveAtVelocity(lateral_mot, kcdc.MOT_Reverse)
        lat_moving = True

def release_right(e):
    global move_mode, lateral_mot, lat_moving
    if move_mode == MoveMode.CONTINUOUS:
        kcdc.CC_StopProfiled(lateral_mot)
    lat_moving = False

def move_up(e):
    global move_mode, longitudinal_mot, long_moving
    if move_mode == MoveMode.JOG:
        kcdc.CC_MoveJog(longitudinal_mot, kcdc.MOT_Reverse)
        long_moving = True
    if move_mode == MoveMode.CONTINUOUS and long_moving == False:
        kcdc.CC_MoveAtVelocity(longitudinal_mot, kcdc.MOT_Reverse)
        long_moving = True

def release_up(e):
    global move_mode, longitudinal_mot, long_moving
    if move_mode == MoveMode.CONTINUOUS:
       kcdc.CC_StopProfiled(longitudinal_mot)
    long_moving = False

def move_down(e):
    global move_mode, longitudinal_mot, long_moving
    if move_mode == MoveMode.JOG:
        kcdc.CC_MoveJog(longitudinal_mot, kcdc.MOT_Forwards)
        long_moving = True
    if move_mode == MoveMode.CONTINUOUS and long_moving == False:
        kcdc.CC_MoveAtVelocity(longitudinal_mot, kcdc.MOT_Forwards)
        long_moving = True

def release_down(e):
    global move_mode, longitudinal_mot, long_moving
    if move_mode == MoveMode.CONTINUOUS:
        kcdc.CC_StopProfiled(longitudinal_mot)
    long_moving = False

# def set_rotation_mode(e):
#     kcdc.CC_SetRotationModes(lateral_mot, MOT_MovementModes.RotationalWrapping.value, MOT_MovementDirections.Forwards.value)
#     kcdc.CC_SetRotationModes(lateral_mot, MOT_MovementModes.RotationalWrapping.value, MOT_MovementDirections.Reverse.value)
#     kcdc.CC_SetRotationModes(longitudinal_mot, MOT_MovementModes.RotationalWrapping.value, MOT_MovementDirections.Forwards.value)
#     kcdc.CC_SetRotationModes(longitudinal_mot, MOT_MovementModes.RotationalWrapping.value, MOT_MovementDirections.Reverse.value)
#     print('rotation mode set')

def rotate_cw(e):
     print ('rotate cw')
#     global move_mode, lateral_mot, lat_moving
#     if move_mode == MoveMode.JOG and lat_moving == False:
#         kcdc.CC_SetRotationModes(lateral_mot, MOT_MovementModes.RotationalWrapping.value, MOT_MovementDirections.Forwards.value)
#         long_moving = True
#     if move_mode == MoveMode.CONTINUOUS:
#         kcdc.CC_SetRotationModes(lateral_mot, MOT_MovementModes.RotationalWrapping.value, MOT_MovementDirections.Forwards.value)
#         print('move cw')

def release_cw(e):
    global move_mode, lateral_mot, lat_moving
    if move_mode == MoveMode.CONTINUOUS:
        print('stopping move cw')

def rotate_ccw(e):
     print('rotate ccw')
#     global move_mode, longitudinal_mot, long_moving
#     if move_mode == MoveMode.JOG:
#         kcdc.CC_SetRotationModes(longitudinal_mot, MOT_MovementModes.RotationalWrapping.value, MOT_MovementDirections.Forwards.value)
#     if move_mode == MoveMode.CONTINUOUS:
#         kcdc.CC_SetRotationModes(longitudinal_mot, MOT_MovementModes.RotationalWrapping.value, MOT_MovementDirections.Forwards.value)

def release_ccw(e):
    global move_mode, longitudinal_mot, long_moving
    if move_mode == MoveMode.CONTINUOUS:
        print('stopping move ccw')

def stop_all(e):
    if move_mode == MoveMode.CONTINUOUS or move_mode == MoveMode.JOG:
        kcdc.CC_StopImmediate(lateral_mot)
        kcdc.CC_StopImmediate(longitudinal_mot)
    # We may also want an "Emergency Stop All" button, perhaps the spacebar, that
    # uses CC_StopImmediate and stops the motion of all stages.

def jog_mode(e):
    global move_mode
    move_mode = MoveMode.JOG
    print('JOG mode activated')

def set_jog_mode(e):
    kcdc.CC_SetJogMode(lateral_mot, kcdc.MOT_JogModes.MOT_SingleStep.value, kcdc.MOT_StopModes.MOT_Profiled.value)
    kcdc.CC_SetJogMode(longitudinal_mot, kcdc.MOT_JogModes.MOT_SingleStep.value, kcdc.MOT_StopModes.MOT_Profiled.value)
    print('JOG mode set')

def set_jog_step():
    step = float(input('New jog step size (mm):'))
    kcdc.CC_SetJogStepSize(lateral_mot, mm_to_steps(step))
    kcdc.CC_SetJogStepSize(longitudinal_mot, mm_to_steps(step))

def cont_mode(e):
    global move_mode
    move_mode = MoveMode.CONTINUOUS
    print('CONTINUOUS mode activated')

def set_velocity():
    vel = float(input('New velocity (device units):'))

help_txt = """\nControls\n--------\n
\tleft arrow - move left
\tright arrow - move right
\tdown arrow - move down
\tup arrow - move up
\ts - reset jog
\tj - jog mode
\tshift + j - jog step size
\tk - continuous mode
\tc - clockwise rotation
\tx - counterclockwise rotation
\tspacebar - emergency stop all
\th - help
\tq - quit
"""

def helpme(e):
    global help_txt
    print(help_txt)

keyboard.on_press_key('left arrow', move_left)
keyboard.on_release_key('left arrow', release_left)
keyboard.on_press_key('right arrow', move_right)
keyboard.on_release_key('right arrow', release_right)
keyboard.on_press_key('up arrow', move_up)
keyboard.on_release_key('up arrow', release_up)
keyboard.on_press_key('down arrow', move_down)
keyboard.on_release_key('down arrow', release_down)
keyboard.on_press_key('c', rotate_cw)
keyboard.on_release_key('c', release_cw)
keyboard.on_press_key('x', rotate_ccw)
keyboard.on_release_key('x', release_ccw)
keyboard.on_press_key('s', set_jog_mode)
keyboard.on_press_key('j', jog_mode)
keyboard.add_hotkey('shift + j', set_jog_step)
keyboard.on_press_key('k', cont_mode)
keyboard.add_hotkey('shift + k', set_velocity)
keyboard.on_press_key('space', stop_all)
keyboard.on_press_key('h', helpme)

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

    # Default configuration for jogging motors
    kcdc.CC_SetJogStepSize(lateral_mot, mm_to_steps(STEP_SIZE_MM))
    kcdc.CC_SetJogStepSize(longitudinal_mot, mm_to_steps(STEP_SIZE_MM))

    print(help_txt)
    input('Press <ENTER> to active motion...')

    while True:
        if keyboard.is_pressed('q'):
            print("QUIT")
            break
