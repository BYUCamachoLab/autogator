# -*- coding: utf-8 -*-
#
# Copyright © Autogator Project Contributors
# Licensed under the terms of the GNU GPLv3+ License
# (see autogator/__init__.py for details)

import os

os.environ["PATH"] = "C:\\Program Files\\ThorLabs\\Kinesis" + ";" + os.environ["PATH"]

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

# -------------------------------------------------------------------
# User defined variables

# Optimization type, one of:
#   nm : Nelder-Mead
#   slsqp : Sequential Least Squares Programming algorithm
#   lbfgsb : lbfgsb algorithm
#   de : Differential Evolution
#   brute : brute force (check every point in grid)
OPT_TYPE = "slsqp"

# Bounds: bounding box for optimization, centered around the
# probe's starting position, in mm or degrees (global optimizer only)
lat_bound = (-0.020, 0.020)  # Lateral bounds, mm
long_bound = (-0.020, 0.020)  # Longitudinal bounds, mm
rot_bound = (0, 0)  # Rotational bounds, degrees
# -------------------------------------------------------------------

STEPS_PER_MM = 34304
STEPS_PER_DEG = 2000


def mm_to_steps(mm):
    return round(mm * STEPS_PER_MM)


def steps_to_mm(steps):
    return steps / STEPS_PER_MM


def deg_to_steps(deg):
    return round(deg * STEPS_PER_DEG)


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
    x = np.round(x).astype(int)
    kcdc.CC_MoveToPosition(lateral_mot, c_int(x[0]))
    kcdc.CC_MoveToPosition(longitudinal_mot, c_int(x[1]))
    kcdc.CC_MoveToPosition(rotational, c_int(x[2]))
    block(lateral_mot)
    block(longitudinal_mot)
    block(rotational)
    data = float(scope.query("MEAS1:RES:ACT?"))
    print("x:", x, "value:", data)
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
        # Get Motor Position
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
    kcdc.CC_WaitForMessage(
        serialno, byref(message_type), byref(message_id), byref(message_data)
    )
    while (int(message_type.value) != 2) or (int(message_id.value) != 1):
        kcdc.CC_WaitForMessage(
            serialno, byref(message_type), byref(message_id), byref(message_data)
        )


def optimize(method, x0, bounds):
    if method == "nm":
        res = minimize(
            J,
            np.array(x0),
            method="nelder-mead",
            options={"xatol": 0.2, "fatol": 10, "disp": True},
        )
    elif method == "lbfgsb":
        res = minimize(J, np.array(x0), method="L-BFGS-B", bounds=bounds)
    elif method == "slsqp":
        res = minimize(J, np.array(x0), method="SLSQP", bounds=bounds)
    elif method == "de":
        res = differential_evolution(J, bounds)
    else:
        raise ValueError(
            'OPT_TYPE is not one of "local" or "global", is it defined correctly?'
        )
    return res


if kcdc.TLI_BuildDeviceList() == 0:
    print("Device list built (no errors).")

    size = kcdc.TLI_GetDeviceListSize()
    print(size, "device(s) found.")

    serialnos = create_string_buffer(100)
    kcdc.TLI_GetDeviceListByTypeExt(serialnos, 100, 27)
    serialnos = list(filter(None, serialnos.value.decode("utf-8").split(",")))
    print("Serial #'s:", serialnos)

    # Open Communication
    rm = visa.ResourceManager()
    scope = rm.open_resource("TCPIP::10.32.112.162::INSTR")
    open_motors()

    # Calculate current position
    pos_du = []
    for motor in motors:
        kcdc.CC_RequestPosition(motor)
        pos_du.append(kcdc.CC_GetPosition(motor))
    print("Current position: {}, {}, {}".format(*pos_du))

    # Calculate bounds in device units
    bounds_du = []
    lb, ub = lat_bound
    bounds_du.append((mm_to_steps(lb) + pos_du[0], mm_to_steps(ub) + pos_du[0]))
    lb, ub = long_bound
    bounds_du.append((mm_to_steps(lb) + pos_du[1], mm_to_steps(ub) + pos_du[1]))
    lb, ub = rot_bound
    bounds_du.append((deg_to_steps(lb) + pos_du[2], deg_to_steps(ub) + pos_du[2]))
    print("Bounds:", bounds_du)
    x = input("Press <ENTER> to begin moving...")

    # Configure motors for position movement speed

    # Wake up, scope!
    try:
        scope.write("TIM:SCAL 1e-9")  # Set the time base of the oscilloscope
        scope.write("MEAS1:SOUR C1W1")  # Set measuring params
        scope.write("MEAS1 ON")
        scope.write(
            "MEAS1:MAIN MAX"
        )  # Measure the max value in the current view window (Based on time base)
        scope.write("CHAN1:RANG 22")  # Horizontal range 22V
        scope.write("CHAN1:POS 0")  # Offset 0
        scope.write("CHAN1:COUP DCL")  # Coupling DC 1MOhm
        scope.write("CHAN1:STAT ON")  # Switch Channel 1 ON
        scope.query("*OPC?")
        scope.ext_error_checking()

        # Start Optimization
        res = optimize(OPT_TYPE, pos_du, bounds_du)
        print(res.x)

        # fig, ax = plt.subplots(1,1)
        # im = ax.imshow(data, cmap='hot')
        # im.set_data(data)
        # im.set_clim(data.min(), data.max())
        # fig.canvas.draw_idle()
        # plt.pause(0.000001)
        # plt.show()

    except VISAresourceExtentions.InstrumentErrorException as e:
        # Catching instrument error exception and showing its content
        print("Instrument error(s) occurred:\n" + e.message)
