# -*- coding: utf-8 -*-
#
# Copyright © Autogator Project Contributors
# Licensed under the terms of the MIT License
# (see autogator/__init__.py for details)

import os
os.environ['PATH'] = "C:\\Program Files\\ThorLabs\\Kinesis" + ";" + os.environ['PATH']

from threading import Thread
import time
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

import thorlabs_kinesis as tk
from thorlabs_kinesis import kcube_dcservo as kcdc

from autogator.models.stage import Z825B, VariableRotationalMotor


if kcdc.TLI_BuildDeviceList() == 0:
    print("Device list built (no errors).")

    size = kcdc.TLI_GetDeviceListSize()
    print(size, "device(s) found.")

    serialnos = create_string_buffer(100)
    kcdc.TLI_GetDeviceListByTypeExt(serialnos, 100, 27)
    serialnos = list(filter(None, serialnos.value.decode("utf-8").split(',')))
    print("Serial #'s:", serialnos)

    lateral = Z825B(27504851)
    longitudinal = Z825B(27003497)
    rotational = VariableRotationalMotor(27003366)

    # accel_param = c_int()
    # vel_param = c_int()
    # message_type = WORD()
    # message_id = WORD()
    # message_data = DWORD()
    # current_motor_pos = 0

    # motor_command = c_int(2000)

    # # Open Communication
    # kcdc.CC_Open(serialno)
    # kcdc.CC_StartPolling(serialno, c_int(20))
    # kcdc.CC_ClearMessageQueue(serialno)
    # time.sleep(3)
    # homeable = bool(kcdc.CC_CanHome(serialno))
    # print(homeable)
    # #Get Motor Position
    # kcdc.CC_GetJogVelParams(serialno, byref(accel_param), byref(vel_param))
    # #print(accel_param.value)
    # current_motor_pos = kcdc.CC_GetPosition(serialno)
    # print(current_motor_pos)
    # # #kcdc.CC_Home(serialno)

    # # Start Move Test
    # kcdc.CC_ClearMessageQueue(serialno)
    # kcdc.CC_MoveToPosition(serialno, motor_command)
    # kcdc.CC_WaitForMessage(serialno, byref(message_type), byref(message_id), byref(message_data))

    # while (int(message_type.value) != 2) or (int(message_id.value) != 1):
    #     kcdc.CC_WaitForMessage(serialno, byref(message_type), byref(message_id), byref(message_data))
    #     kcdc.CC_RequestPosition(serialno)
    #     # I Get correct position feedback here
    #     print("TEST", kcdc.CC_GetPosition(serialno))

    # # But I dont get correct position feedback here. I just get 0.
    # kcdc.CC_RequestPosition(serialno)
    # time.sleep(0.1)
    # current_motor_pos = kcdc.CC_GetPosition(serialno)
    # print(current_motor_pos)
    # # Close Communication
    # kcdc.CC_StopPolling(serialno)
    # kcdc.CC_Close(serialno)
