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
    num_passes = 10 # number of passes the array will take across the chip (Latitudinal Stage)
    num_samples = 10 # number of samples per pass (Longitudinal Stage)
    lat_step = 1 # step size between vertical/latitudinal scan passes in mm 
    long_step = 1 # step size between horizontal/longitudinal scan positions in mm
    max_lat_travel = num_passes * lat_step * steps_per_mm
    max_long_travel = num_samples * long_step * steps_per_mm

arr = np.zeros((num_passes,num_samples)) # array to store data

if kcdc.TLI_BuildDeviceList() == 0:
    print("Device list built (no errors).")

    size = kcdc.TLI_GetDeviceListSize()
    print(size, "device(s) found.")

    serialnos = create_string_buffer(100)
    kcdc.TLI_GetDeviceListByTypeExt(serialnos, 100, 27)
    serialnos = list(filter(None, serialnos.value.decode("utf-8").split(',')))
    print("Serial #'s:", serialnos)

    lateral = c_char_p(bytes("27504851", "utf-8"))
    longitudinal = c_char_p(bytes("27003497", "utf-8"))
    rotational = c_char_p(bytes("27003366", "utf-8"))

    motors = [lateral, longitudinal, rotational]

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
        kcdc.CC_Home(serialno)
    
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
                test_pos = kcdc.CC_GetPosition(longitudinal)
                if p%2==0:
                    current_long_pos = max_long_travel - (p*long_step*steps_per_mm)
                    kcdc.CC_MoveToPosition(longitudinal, c_int(max_long_travel-(p*long_step*steps_per_mm)))
                    kcdc.CC_WaitForMessage(longintudinal_mot, byref(message_type), byref(message_id), byref(message_data))
                    while (int(message_type.value) != 2) or (int(message_id.value) != 1):
                        kcdc.CC_WaitForMessage(longitudinal, byref(message_type), byref(message_id), byref(message_data))
                        #kcdc.CC_RequestPosition(serialno)
                    time.sleep(0.01)
                    arr[i][max_long_pos-p] = scope.query('MEAS1:RES:ACT?')
                    #time.sleep(0.01)
                else:
                    current_long_pos = p*long_step*steps_per_mm
                    kcdc.CC_MoveToPosition(longitudinal, c_int(current_long_pos+(p*long_step*steps_per_mm)))
                    while (int(message_type.value) != 2) or (int(message_id.value) != 1):
                        kcdc.CC_WaitForMessage(longitudinal, byref(message_type), byref(message_id), byref(message_data))
                        #kcdc.CC_RequestPosition(serialno)
                    time.sleep(0.01)
                    arr[i][p] = scope.query('MEAS1:RES:ACT?')
                    #time.sleep(0.01)

            current_lat_pos = i*lat_steps*steps_per_mm
            kcdc.CC_MoveToPosition(lateral, c_int(i*lat_step*steps_per_mm))
            kcdc.CC_WaitForMessage(lateral, byref(message_type), byref(message_id), byref(message_data))
            while (int(message_type.value) != 2) or (int(message_id.value) != 1):
                kcdc.CC_WaitForMessage(lateral, byref(message_type), byref(message_id), byref(message_data))
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


