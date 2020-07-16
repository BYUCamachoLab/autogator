# -*- coding: utf-8 -*-
#
# Copyright © Autogator Project Contributors
# Licensed under the terms of the MIT License
# (see autogator/__init__.py for details)

import os
os.environ['PATH'] = "C:\\Program Files\\ThorLabs\\Kinesis" + ";" + os.environ['PATH']

import pyvisa as visa
import VISAresourceExtentions
from pathlib import Path
import time
import math
import numpy as np
import matplotlib.pyplot as plt
import thorlabs_kinesis as tk
from thorlabs_kinesis import kcube_dcservo as kcdc
from autogator.models.stage import Z825B, VariableRotationalMotor

# from threading import Thread

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

STEPS_PER_MM = 34304
SWEEP_DIST_MM = 10.0
STEP_SIZE_MM = 0.5

class Static_Vars:
    ##   ***IMPORTANT: THE MAX TRAVEL ON THE LINEAR STAGE IS 25MM, SO KEEP THE MAX SCAN DISTANCE IN EITHER DIRECTION UNDER 12.5MM***
    steps_per_mm = 34304
     # number of samples per pass (Longitudinal Stage)
    lat_step = 0.1 # step size between vertical/latitudinal scan passes in mm
    long_step = 0.1 # step size between horizontal/longitudinal scan positions in mm
    max_lat_travel = 5
    #num_passes * lat_step * steps_per_mm
    max_long_travel = 5
    num_passes =  math.floor(max_lat_travel/lat_step)
    num_samples = math.floor(max_long_travel/long_step)
    #num_samples * long_step * steps_per_mm

arr = np.zeros((Static_Vars.num_passes,Static_Vars.num_samples)) # array to store data
message_type = WORD()
message_id = WORD()
message_data = DWORD()

if kcdc.TLI_BuildDeviceList() == 0:
    print("Device list built (no errors).")

    size = kcdc.TLI_GetDeviceListSize()
    print(size, "device(s) found.")

    serialnos = create_string_buffer(100)
    kcdc.TLI_GetDeviceListByTypeExt(serialnos, 100, 27)
    serialnos = list(filter(None, serialnos.value.decode("utf-8").split(',')))
    print("Serial #'s:", serialnos)

    lateral_mot = c_char_p(bytes("27504851", "utf-8"))
    longitudinal_mot = c_char_p(bytes("27003497", "utf-8"))
    rotational = c_char_p(bytes("27003366", "utf-8"))

    motors = [lateral_mot, longitudinal_mot, rotational]

    # message_type = WORD()
    # message_id = WORD()
    # message_data = DWORD()
    # current_motor_pos = 0

    # motor_command = c_int(2000)

    # Open Communication

    rm = visa.ResourceManager()
    scope = rm.open_resource('TCPIP::10.32.112.162::INSTR')

    for serialno in motors:
        kcdc.CC_Open(serialno)
        kcdc.CC_StartPolling(serialno, c_int(20))
        kcdc.CC_ClearMessageQueue(serialno)
        time.sleep(3)
        homeable = bool(kcdc.CC_CanHome(serialno))
        print("Can home:", homeable)
        #Get Motor Position
        accel_param, vel_param = c_int(), c_int()
        kcdc.CC_GetJogVelParams(serialno, byref(accel_param), byref(vel_param))
        print("Acceleration:", accel_param.value, "Velocity:", vel_param.value)
        current_motor_pos = kcdc.CC_GetPosition(serialno)
        print("Position:", current_motor_pos)
        #kcdc.CC_Home(serialno)

    kcdc.CC_RequestPosition(lateral_mot)
    current_lat_pos = kcdc.CC_GetPosition(lateral_mot)
    kcdc.CC_RequestPosition(longitudinal_mot)
    current_long_pos = kcdc.CC_GetPosition(longitudinal_mot)
    
    print(current_lat_pos)
    print(current_long_pos)

    
    corner_lat_pos = current_lat_pos-(math.floor(Static_Vars.max_lat_travel*Static_Vars.steps_per_mm/2))
    corner_long_pos = current_long_pos-(math.floor(Static_Vars.max_long_travel*Static_Vars.steps_per_mm/2))
    print(corner_lat_pos)
    print(corner_long_pos)
    x = input("TEST")

    kcdc.CC_MoveToPosition(longitudinal_mot, c_int(corner_long_pos))
    kcdc.CC_MoveToPosition(lateral_mot, c_int(corner_lat_pos))
    while (int(message_type.value) != 2) or (int(message_id.value) != 1):
        kcdc.CC_WaitForMessage(longitudinal_mot, byref(message_type), byref(message_id), byref(message_data))
    time.sleep(0.02)
        

    
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
        for i in range(len(arr)):
            for p in range(len(arr[0])):
                if i%2==1:
                    next_pos=math.floor(corner_long_pos+(Static_Vars.max_long_travel*Static_Vars.steps_per_mm)-(p*Static_Vars.long_step*Static_Vars.steps_per_mm))
                    kcdc.CC_MoveToPosition(longitudinal_mot, c_int(next_pos))
                    kcdc.CC_WaitForMessage(longitudinal_mot, byref(message_type), byref(message_id), byref(message_data))
                    while (int(message_type.value) != 2) or (int(message_id.value) != 1):
                        kcdc.CC_WaitForMessage(longitudinal_mot, byref(message_type), byref(message_id), byref(message_data))
                        #kcdc.CC_RequestPosition(serialno)
                    time.sleep(0.01)
                    arr[i-1][Static_Vars.num_samples-p-1] = scope.query('MEAS1:RES:ACT?')
                    #time.sleep(0.01)
                else:
                    next_pos=math.floor(corner_long_pos+(p*Static_Vars.long_step*Static_Vars.steps_per_mm))
                    kcdc.CC_MoveToPosition(longitudinal_mot, c_int(next_pos))
                    while (int(message_type.value) != 2) or (int(message_id.value) != 1):
                        kcdc.CC_WaitForMessage(longitudinal_mot, byref(message_type), byref(message_id), byref(message_data))
                        #kcdc.CC_RequestPosition(serialno)
                    time.sleep(0.01)
                    arr[i-1][p-1] = scope.query('MEAS1:RES:ACT?')
                    #time.slee0.01)

            current_lat_pos = i*Static_Vars.lat_step*Static_Vars.steps_per_mm
            next_pos=math.floor(corner_lat_pos+(i*Static_Vars.lat_step*Static_Vars.steps_per_mm))
            kcdc.CC_MoveToPosition(lateral_mot, c_int(next_pos))
            kcdc.CC_WaitForMessage(lateral_mot, byref(message_type), byref(message_id), byref(message_data))
            while (int(message_type.value) != 2) or (int(message_id.value) != 1):
                kcdc.CC_WaitForMessage(lateral_mot, byref(message_type), byref(message_id), byref(message_data))
                #kcdc.CC_RequestPosition(serialno)
        
        


        # kcdc.CC_ClearMessageQueue(serialno)
        # #kcdc.CC_MoveToPosition(serialno, motor_command)
        # kcdc.CC_WaitForMessage(serialno, byref(message_type), byref(message_id), byref(message_data))
        # while (int(message_type.value) != 2) or (int(message_id.value) != 1):
        #     kcdc.CC_WaitForMessage(serialno, byref(message_type), byref(message_id), byref(message_data))
        #     kcdc.CC_RequestPosition(serialno)


        #     # I Get correct position feedback here
        #     print("TEST", kcdc.CC_GetPosition(serialno))

        # kcdc.CC_RequestPosition(serialno)
        # time.sleep(0.1)
        # current_motor_pos = kcdc.CC_GetPosition(serialno)
        # print(current_motor_pos)
        
        # Close Communication

    except VISAresourceExtentions.InstrumentErrorException as e:
        # Catching instrument error exception and showing its content
        print('Instrument error(s) occurred:\n' + e.message)

    for serialno in motors:
        kcdc.CC_StopPolling(serialno)
        kcdc.CC_Close(serialno)
print(arr)


