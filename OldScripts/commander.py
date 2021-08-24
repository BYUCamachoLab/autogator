# -*- coding: utf-8 -*-
#
# Copyright © Autogator Project Contributors
# Licensed under the terms of the MIT License
# (see autogator/__init__.py for details)

import os

os.environ["PATH"] = "C:\\Program Files\\ThorLabs\\Kinesis" + ";" + os.environ["PATH"]

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
    num_passes = (
        10  # number of passes the array will take across the chip (Latitudinal Stage)
    )
    num_samples = 10  # number of samples per pass (Longitudinal Stage)
    lat_step = 1  # step size between vertical/latitudinal scan passes in mm
    long_step = 1  # step size between horizontal/longitudinal scan positions in mm
    max_lat_travel = num_passes * lat_step * steps_per_mm
    max_long_travel = num_samples * long_step * steps_per_mm


arr = np.zeros((Static_Vars.num_passes, Static_Vars.num_samples))  # array to store data
message_type = WORD()
message_id = WORD()
message_data = DWORD()

long_pos = int(input("Longitudinal Position:"))
lat_pos = int(input("Lateral Position:"))
rot_pos = int(input("Rotational Position:"))

if kcdc.TLI_BuildDeviceList() == 0:
    print("Device list built (no errors).")

    size = kcdc.TLI_GetDeviceListSize()
    print(size, "device(s) found.")

    serialnos = create_string_buffer(100)
    kcdc.TLI_GetDeviceListByTypeExt(serialnos, 100, 27)
    serialnos = list(filter(None, serialnos.value.decode("utf-8").split(",")))
    print("Serial #'s:", serialnos)

    lateral_mot = c_char_p(bytes("27504851", "utf-8"))
    longitudinal_mot = c_char_p(bytes("27003497", "utf-8"))
    rotational = c_char_p(bytes("27003366", "utf-8"))

    motors = [lateral_mot, longitudinal_mot, rotational]

    for serialno in motors:
        kcdc.CC_Open(serialno)
        kcdc.CC_StartPolling(serialno, c_int(20))
        kcdc.CC_ClearMessageQueue(serialno)
        time.sleep(3)
        homeable = bool(kcdc.CC_CanHome(serialno))
        print("Can home:", homeable)
        # Get Motor Position
        accel_param, vel_param = c_int(), c_int()
        kcdc.CC_GetJogVelParams(serialno, byref(accel_param), byref(vel_param))
        print("Acceleration:", accel_param.value, "Velocity:", vel_param.value)
        current_motor_pos = kcdc.CC_GetPosition(serialno)
        print("Position:", current_motor_pos)

    # message_type = WORD()
    # message_id = WORD()
    # message_data = DWORD()
    # current_motor_pos = 0

    # motor_command = c_int(2000)

    kcdc.CC_MoveToPosition(longitudinal_mot, c_int(long_pos))
    time.sleep(1)
    print("Longitudinal moved.")

    kcdc.CC_MoveToPosition(lateral_mot, c_int(lat_pos))
    time.sleep(1)
    print("Lateral moved.")

    kcdc.CC_MoveToPosition(rotational, c_int(rot_pos))
    time.sleep(1)
    print("Rotational moved.")

    for serialno in motors:
        kcdc.CC_StopPolling(serialno)
        kcdc.CC_Close(serialno)
