# -*- coding: utf-8 -*-
#
# Copyright © Autogator Project Contributors
# Licensed under the terms of the MIT License
# (see autogator/__init__.py for details)

import os
os.environ['PATH'] = "C:\\Program Files\\ThorLabs\\Kinesis" + ";" + os.environ['PATH']

import atexit
import math
from pathlib import Path
import time

import matplotlib.pyplot as plt
import numpy as np
import pyvisa as visa
import thorlabs_kinesis as tk
import VISAresourceExtentions
from scipy.optimize import rosen, minimize, differential_evolution
from thorlabs_kinesis import kcube_dcservo as kcdc

from autogator.models.stage import Z825B, VariableRotationalMotor

from ctypes import (
    c_short,
    c_char_p,
    c_void_p,
    byref,
    c_int,
    create_string_buffer,
)
from ctypes.wintypes import (
    DWORD,
    WORD,
)

SWEEP_DIST_MM = 0.03
STEP_SIZE_MM = 0.001

STEPS_PER_MM = 34304
SHAPE = round(SWEEP_DIST_MM / STEP_SIZE_MM)

def mm_to_steps(mm):
    return round(mm * STEPS_PER_MM)

def steps_to_mm(steps):
    return steps / STEPS_PER_MM

lateral_mot = c_char_p(bytes("27504851", "utf-8"))
longitudinal_mot = c_char_p(bytes("27003497", "utf-8"))
rotational = c_char_p(bytes("27003366", "utf-8"))
motors = [lateral_mot, longitudinal_mot, rotational]

def J(x):
    """
    x is a numpy array with the following structure:
        x[0]: lateral position
        x[1]: longitudinal position
        x[2]: rotational position
    """
    kcdc.CC_MoveToPosition(lateral_mot, c_int(x[0]))
    kcdc.CC_MoveToPosition(longitudinal_mot, c_int(x[1]))
    kcdc.CC_MoveToPosition(rotational, c_int(x[2]))
    block(lateral_mot)
    block(longitudinal_mot)
    block(rotational)
    data = scope.query('MEAS1:RES:ACT?')
    return -1 * data


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

    # Open Communication
    rm = visa.ResourceManager()
    scope = rm.open_resource('TCPIP::10.32.112.162::INSTR')
    open_motors()

    # Calculate current position
    kcdc.CC_RequestPosition(lateral_mot)
    current_lat_pos_du = kcdc.CC_GetPosition(lateral_mot)
    kcdc.CC_RequestPosition(longitudinal_mot)
    current_long_pos_du = kcdc.CC_GetPosition(longitudinal_mot)
    print("Current position: {}, {}".format(current_lat_pos_du, current_long_pos_du))

    # Calculate starting position
    corner_lat_pos_du = current_lat_pos_du - mm_to_steps(SWEEP_DIST_MM / 2)
    corner_long_pos_du = current_long_pos_du - mm_to_steps(SWEEP_DIST_MM / 2)
    print("Corner position: {}, {}".format(corner_lat_pos_du, corner_long_pos_du))
    x = input("Press <ENTER> to begin moving...")

    # Move to starting position
    kcdc.CC_MoveToPosition(lateral_mot, c_int(corner_lat_pos_du))
    kcdc.CC_MoveToPosition(longitudinal_mot, c_int(corner_long_pos_du))
    block(longitudinal_mot)
    block(lateral_mot)

    # Configure motors for jogging
    kcdc.CC_SetJogStepSize(lateral_mot, mm_to_steps(STEP_SIZE_MM))
    kcdc.CC_SetJogStepSize(longitudinal_mot, mm_to_steps(STEP_SIZE_MM))
        
    # Wake up, scope!
    try: 
        scope.write('TIM:SCAL 1e-9') # Set the time base of the oscilloscope
        scope.write('MEAS1:SOUR C1W1') # Set measuring params
        scope.write('MEAS1 ON')
        scope.write('MEAS1:MAIN MAX') # Measure the max value in the current view window (Based on time base)
        scope.write('CHAN1:RANG 22')  # Horizontal range 22V
        scope.write('CHAN1:POS 0')  # Offset 0
        scope.write('CHAN1:COUP DCL')  # Coupling DC 1MOhm
        scope.write('CHAN1:STAT ON')  # Switch Channel 1 ON
        scope.query('*OPC?')
        scope.ext_error_checking()

        # Start Move Test
        rows, cols = data.shape
        
        fig, ax = plt.subplots(1,1)
        im = ax.imshow(data, cmap='hot')
        
        for i in range(rows):
            for j in range(cols):
                # Measure and jog the longitudinal motor
                data[i, j] = scope.query('MEAS1:RES:ACT?')
                kcdc.CC_MoveJog(longitudinal_mot, kcdc.MOT_TravelDirection.MOT_Reverse.value)

                im.set_data(data)
                im.set_clim(data.min(), data.max())
                fig.canvas.draw_idle()
                plt.pause(0.000001)
                
                block(longitudinal_mot)
            
            # Jog the lateral motor
            kcdc.CC_MoveJog(lateral_mot, kcdc.MOT_TravelDirection.MOT_Reverse.value)
            block(lateral_mot)
            
            # Move the longitudinal motor back to the start of the row
            kcdc.CC_MoveToPosition(longitudinal_mot, c_int(corner_long_pos_du))
            block(longitudinal_mot)

        plt.show()

        with open('data.npy', 'wb') as f:
            np.save(f, data)
        
    except VISAresourceExtentions.InstrumentErrorException as e:
        # Catching instrument error exception and showing its content
        print('Instrument error(s) occurred:\n' + e.message)

    # Move to original position
    kcdc.CC_MoveToPosition(lateral_mot, c_int(current_lat_pos_du))
    kcdc.CC_MoveToPosition(longitudinal_mot, c_int(corner_long_pos_du))
    block(longitudinal_mot)
    block(lateral_mot)
