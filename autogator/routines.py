# -*- coding: utf-8 -*-
#
# Copyright © Autogator Project Contributors
# Licensed under the terms of the MIT License
# (see autogator/__init__.py for details)

"""
Routines
========

A set of common, useful stage operations implemented using common calls from 
abstracted motors and auxiliary devices. In theory, setups utilizing different
hardware should be able to use the same routines without any modification.
"""

import os
import logging
import threading
import time
from typing import Callable, List, Tuple

import numpy as np
import matplotlib.pyplot as plt
from autogator.circuit import Circuit
import keyboard
from pydantic import BaseModel, BaseSettings

from autogator.hardware import DataAcquisitionUnitBase, Stage


log = logging.getLogger(__name__)


class KeyloopKeyboardBindings(BaseSettings):
    MOVE_LEFT: str = "left arrow"
    MOVE_RIGHT: str = "right arrow"
    MOVE_UP: str = "up arrow"
    MOVE_DOWN: str = "down arrow"
    JOG_LEFT: str = "a"
    JOG_RIGHT: str = "d"
    JOG_UP: str = "w"
    JOG_DOWN: str = "s"
    JOG_CLOCKWISE: str = "c"
    JOG_COUNTERCLOCKWISE: str = "x"
    LINEAR_JOG_STEP: str = "shift + j"
    ROTATIONAL_JOG_STEP: str = "shift + g"
    STOP_ALL: str = "space"
    HOME: str = "o"
    HELP: str = "h"
    QUIT: str = "q"


class KeyboardControl:
    def __init__(self, stage: Stage, bindings: KeyloopKeyboardBindings = None):
        self.stage = stage

        if bindings is None:
            bindings = KeyloopKeyboardBindings()
        self.bindings = bindings

        self.semaphores = {
            "MOTOR_X" : threading.Semaphore(),
            "MOTOR_Y" : threading.Semaphore(),
            "MOTOR_PSI" : threading.Semaphore(),
        }

        self.linear_step_size = 0.1
        self.rotational_step_size = 0.1

    def _move_left(self):
        semaphore = self.semaphores["MOTOR_X"]
        if semaphore.acquire(timeout=0.1):
            self.stage.x.move_cont("backward")
            while keyboard.is_pressed(self.bindings.MOVE_LEFT):
                time.sleep(0.05)
            self.stage.x.stop()
            semaphore.release()

    def _move_right(self):
        semaphore = self.semaphores["MOTOR_X"]
        if semaphore.acquire(timeout=0.1):
            self.stage.x.move_cont("forward")
            while keyboard.is_pressed(self.bindings.MOVE_RIGHT):
                time.sleep(0.05)
            self.stage.x.stop()
            semaphore.release()

    def _move_up(self):
        semaphore = self.semaphores["MOTOR_Y"]
        if semaphore.acquire(timeout=0.1):
            self.stage.y.move_cont("forward")
            while keyboard.is_pressed(self.bindings.MOVE_UP):
                time.sleep(0.05)
            self.stage.y.stop()
            semaphore.release()

    def _move_down(self):
        semaphore = self.semaphores["MOTOR_Y"]
        if semaphore.acquire(timeout=0.1):
            self.stage.y.move_cont("backward")
            while keyboard.is_pressed(self.bindings.MOVE_DOWN):
                time.sleep(0.05)
            self.stage.y.stop()
            semaphore.release()

    def _jog_left(self):
        semaphore = self.semaphores["MOTOR_X"]
        if semaphore.acquire(timeout=0.1):
            self.stage.x.move_by(-self.linear_step_size)
            semaphore.release()

    def _jog_right(self):
        semaphore = self.semaphores["MOTOR_X"]
        if semaphore.acquire(timeout=0.1):
            self.stage.x.move_by(self.linear_step_size)
            semaphore.release()

    def _jog_up(self):
        semaphore = self.semaphores["MOTOR_Y"]
        if semaphore.acquire(timeout=0.1):
            self.stage.y.move_by(self.linear_step_size)
            semaphore.release()

    def _jog_down(self):
        semaphore = self.semaphores["MOTOR_Y"]
        if semaphore.acquire(timeout=0.1):
            self.stage.y.move_by(-self.linear_step_size)
            semaphore.release()

    def _jog_cw(self):
        semaphore = self.semaphores["MOTOR_PSI"]
        if semaphore.acquire(timeout=0.1):
            self.stage.psi.move_by(self.rotational_step_size)
            semaphore.release()

    def _jog_ccw(self):
        semaphore = self.semaphores["MOTOR_PSI"]
        if semaphore.acquire(timeout=0.1):
            self.stage.psi.move_by(-self.rotational_step_size)
            semaphore.release()

    def _set_linear_jog_step(self):
        val = None
        while val is None:
            answer = input(f"Enter new step size or [ENTER] to cancel (current {self.linear_step_size}): ")
            if answer == "n":
                return
            try:
                val = float(answer)
            except ValueError:
                pass
        self.linear_step_size = val
        print(f"New step size set: {self.linear_step_size}")

    def _set_rotational_jog_step(self):
        val = None
        while val is None:
            answer = input(f"Enter new step size or [ENTER] to cancel (current {self.rotational_step_size}): ")
            if answer == "n":
                return
            try:
                val = float(answer)
            except ValueError:
                pass
        self.rotational_step_size = val
        print(f"New step size set: {self.rotational_step_size}")

    def _home(self):
        confirm = input("Are you sure you want to home? Type 'yes' to confirm: ")
        if confirm != "yes":
            return
        for semaphore in self.semaphores.values():
            semaphore.acquire()
        for motor in self.stage.motors:
            if motor:
                motor.home()
        for semaphore in self.semaphores.values():
            semaphore.release()
        log.info("Homing complete")

    def _help(self):
        print(f"""
        Stage Control
        -------------
        move left: {self.bindings.MOVE_LEFT}
        move right: {self.bindings.MOVE_RIGHT}
        move up: {self.bindings.MOVE_UP}
        move down: {self.bindings.MOVE_DOWN}
        jog left: {self.bindings.JOG_LEFT}
        jog right: {self.bindings.JOG_RIGHT}
        jog up: {self.bindings.JOG_UP}
        jog down: {self.bindings.JOG_DOWN}
        jog clockwise: {self.bindings.JOG_CLOCKWISE}
        jog counterclockwise: {self.bindings.JOG_COUNTERCLOCKWISE}
        linear jog step: {self.bindings.LINEAR_JOG_STEP}
        rotational jog step: {self.bindings.ROTATIONAL_JOG_STEP}
        home: {self.bindings.HOME}
        help: {self.bindings.HELP}
        quit: {self.bindings.QUIT}
        """)
        # stop all: {self.bindings.STOP_ALL}

    def loop(self) -> None:
        running = threading.Event()
        running.set()

        actions = list(self.bindings.dict().keys())
        keys = list(self.bindings.dict().values())
        funcs = {
            "MOVE_LEFT": self._move_left,
            "MOVE_RIGHT": self._move_right,
            "MOVE_UP": self._move_up,
            "MOVE_DOWN": self._move_down,
            "JOG_LEFT": self._jog_left,
            "JOG_RIGHT": self._jog_right,
            "JOG_UP": self._jog_up,
            "JOG_DOWN": self._jog_down,
            "JOG_CLOCKWISE": self._jog_cw,
            "JOG_COUNTERCLOCKWISE": self._jog_ccw,
            "LINEAR_JOG_STEP": self._set_linear_jog_step,
            "ROTATIONAL_JOG_STEP": self._set_rotational_jog_step,
            "HOME": self._home,
            "HELP": self._help,
        }
        flags = {binding : threading.Event() for binding in actions}

        # keyboard.add_hotkey(self.bindings.MOVE_LEFT, lambda: self._move_left(semaphores[self.bindings.MOVE_LEFT]))
        keyboard.add_hotkey(self.bindings.MOVE_LEFT, lambda: flags["MOVE_LEFT"].set())
        keyboard.add_hotkey(self.bindings.MOVE_RIGHT, lambda: flags["MOVE_RIGHT"].set())
        keyboard.add_hotkey(self.bindings.MOVE_UP, lambda: flags["MOVE_UP"].set())
        keyboard.add_hotkey(self.bindings.MOVE_DOWN, lambda: flags["MOVE_DOWN"].set())
        keyboard.add_hotkey(self.bindings.JOG_LEFT, lambda: flags["JOG_LEFT"].set())
        keyboard.add_hotkey(self.bindings.JOG_RIGHT, lambda: flags["JOG_RIGHT"].set())
        keyboard.add_hotkey(self.bindings.JOG_UP, lambda: flags["JOG_UP"].set())
        keyboard.add_hotkey(self.bindings.JOG_DOWN, lambda: flags["JOG_DOWN"].set())
        keyboard.add_hotkey(self.bindings.JOG_CLOCKWISE, lambda: flags["JOG_CLOCKWISE"].set())
        keyboard.add_hotkey(self.bindings.JOG_COUNTERCLOCKWISE, lambda: flags["JOG_COUNTERCLOCKWISE"].set())
        keyboard.add_hotkey(self.bindings.LINEAR_JOG_STEP, lambda: flags["LINEAR_JOG_STEP"].set())
        keyboard.add_hotkey(self.bindings.ROTATIONAL_JOG_STEP, lambda: flags["ROTATIONAL_JOG_STEP"].set())
        keyboard.add_hotkey(self.bindings.HOME, lambda: flags["HOME"].set())
        keyboard.add_hotkey(self.bindings.HELP, lambda: flags["HELP"].set())
        keyboard.add_hotkey(self.bindings.QUIT, lambda: running.clear())
        keyboard.add_hotkey(self.bindings.HELP, lambda: flags["HELP"].set())

        def run_flagged():
            for action, flag in flags.items():
                if flag.is_set():
                    t = threading.Thread(target=funcs[action], daemon=True)
                    t.start()
                    flag.clear()

        print("Ready")
        while running.is_set():
            run_flagged()
            time.sleep(0.1)
        # else:
        # clean up all current running actions, make sure all semaphores are freed


def auto_calibration_callback(
    stage: Stage, 
    daq: DataAcquisitionUnitBase, 
    circuit: Circuit, 
    controller: KeyboardControl
) -> None:
    """
    Moves to the specified circuit and optimizes alignment.

    Parameters
    ----------
    """
    print(f"Center {circuit} in view, then quit the controller.")
    controller.loop()

    SCAN_SPAN = 0.025
    SCAN_STEP = 0.005

    print("Optimizing alignment...")
    do_scan = True
    while do_scan:
        auto_scan(stage, daq, SCAN_SPAN, SCAN_STEP, go_to_max=True)
        scan_again = input("Scan again? (y/n) [Enter]: ")
        if scan_again == "y":
            do_scan = True
    print("DONE")


def calibrate(
    stage: Stage, 
    daq: DataAcquisitionUnitBase, 
    circuits: List[Circuit], 
    callback: Callable, 
    controller: KeyboardControl = None
) -> np.ndarray:
    """
    Calculates the calibration for converting from hardware coordinates to GDS coordinates.

    Parameters
    ----------
    stage : Stage
        The stage device to use for calibration.
    daq : DataAcquisitionUnitBase
        The configured data acquisition unit (or class that inherits from 
        :py:class:`DataAcquisitionUnitBase`) to use for calibration.
    circuits : List[Circuit, Circuit, Circuit]
        The three calibration circuits.
    callback : Callable
        A callback function used to optimize at each point. Could be an 
        automatic scan or a function that interacts with the user. It should
        block until the stage has settled on a point, but it does not need to
        return anything; the settled point location will be obtained from the 
        Stage object. It should accept the following parameters, in the 
        corresponding order:
        - stage: The stage object to use for calibration.
        - daq: The data acquisition unit to use for calibration.

    Returns
    -------
    np.ndarray
        The affine transformation matrix that converts from hardware coordinates
        to GDS coordinates.
    """
    # Is this the implementation?
    # https://stackoverflow.com/q/2755771/11530613
    log.debug("Starting calibration")
    if len(circuits) != 3:
        raise ValueError("Expected 3 calibration circuits")

    if controller is None:
        controller = KeyboardControl(stage)

    gds_coords = []
    stage_coords = []
    for i, circuit in enumerate(circuits):
        log.debug("Calibrating circuit %s", str(i+1))
        callback(stage, daq, circuit, controller=controller)
        gds_coords.append(circuit.loc)
        stage_coords.append([stage.x.get_position(), stage.y.get_position()])

    l1, l2, l3 = gds_coords
    gds = np.array(
        [
            [l1.x, l1.y, 1,    0,    0, 0],
            [   0,    0, 0, l1.x, l1.y, 1],
            [l2.x, l2.y, 1,    0,    0, 0],
            [   0,    0, 0, l2.x, l2.y, 1],
            [l3.x, l3.y, 1,    0,    0, 0],
            [   0,    0, 0, l3.x, l3.y, 1],
        ]
    )

    p1, p2, p3 = stage_coords
    stage = np.array(
        [
            [p1[0]],
            [p1[1]],
            [p2[0]],
            [p2[1]],
            [p3[0]],
            [p3[1]],
        ]
    )

    a = np.linalg.inv(gds) @ stage

    conversion_matrix = np.array(
        [
            [a[0][0], a[1][0], a[2][0]], 
            [a[3][0], a[4][0], a[5][0]], 
            [      0,       0,       1],
        ]
    )

    return conversion_matrix


def easy_switcher(
    stage: Stage, 
    daq: DataAcquisitionUnitBase, 
    callback: Callable = None, 
    controller: KeyboardControl = None
) -> None:
    """
    Allows user to set specific locations for easy switching.

    Can provide an optional callback that will be run after the user has moved
    to a given location using the controller. It will be passed ``stage`` and
    ``daq`` as parameters.

    Switching circuits is done by pressing the associated key on the
    keyboard. It is recommended to use one of the numeric keys on the
    keyboard.

    Switching circuits is only available in the context of this function; after
    exiting the loop, location associations are discarded.

    Parameters
    ----------
    stage : Stage
        The stage device to use for interfacing with the hardware.
    daq : DataAcquisitionUnitBase
        The configured data acquisition unit (or class that inherits from
        :py:class:`DataAcquisitionUnitBase`) to use for interfacing with the
        hardware.
    callback : Callable, optional
        A callback function, could be used to optimize at each point. Could be 
        an automatic scan or a function that interacts with the user. It should
        block until the stage has settled on a point, but it does not need to
        return anything; the settled point location will be obtained from the
        Stage object. It should accept the following parameters, in the
        corresponding order:
        - stage: The stage object to use for calibration.
        - daq: The data acquisition unit to use for calibration.
    controller : KeyboardControl, optional
        The controller to use for interfacing with the user. If not provided,
        a default controller will be used.
    """
    again = True
    locs = {}
    while again:
        print(f"Move to first desired location, then quit the controller.")
        controller.loop()

        if callback:
            callback(stage, daq)

        print("Press the key you want to associate this point: ")
        refkey = keyboard.read_hotkey()
        locs[refkey] = [
            stage.x.get_position(),
            stage.y.get_position(),
        ]
        more = input("Log another point? (y, n): ")
        if more != "y":
            again = False

    def go_to_position(x, y):
        stage.set_position(x=x, y=y)

    for key, loc in locs.items():
        keyboard.add_hotkey(key, go_to_position, args=(loc[0], loc[1],))

    controller.loop()


def basic_scan(
    stage: Stage,
    daq: DataAcquisitionUnitBase,
    stage_x: Tuple[float, float] = None,
    stage_y: Tuple[float, float] = None,
    gds_x: Tuple[float, float] = None,
    gds_y: Tuple[float, float] = None,
    stage_center: Tuple[float, float] = None,
    gds_center: Tuple[float, float] = None,
    span: float = None,
    span_x: float = None,
    span_y: float = None,
    step_size: float = None,
    step_size_x: float = None,
    step_size_y: float = None,
    plot: bool = False,
    settle: float = 0.2,
    go_to_max: bool = True,
) -> Tuple[float, Tuple[float, float]]:
    """
    Performs a box scan of given dimensions and goes to position of highest readings returned.

    You must specify one of the following sets of parameters: 
    * ``stage_x`` and ``stage_y``
    * ``gds_x`` and ``gds_y``
    * ``stage_center`` and ``span``
    * ``gds_center`` and ``span``
    * ``span`` (with center not specified, center assumes current location)
    * ``span_x`` and ``span_y`` (with center not specified, center assumes current location)

    Additionally, you must specify one of the following parameter sets:
    * ``step_size``
    * ``step_size_x`` and ``step_size_y``

    Parameters
    ----------
    stage : Stage
        The stage object that provides access to the hardware.
    daq : DataAcquisitionUnitBase
        The preconfigured data acquisition unit to use for taking measurements.
        This function repeatedly calls the 
        :py:func:`DataAcquisitionUnitBase.measure` method to acquire scan data.
    stage_x : Tuple[float, float], optional
        The x-coordinate span of the stage to scan, in motor units, from 
        smallest value to largest.
    stage_y : Tuple[float, float], optional
        The y-coordinate span of the stage to scan, in motor units, from 
        smallest value to largest.
    gds_x : Tuple[float, float], optional
        The x-coordinate span of the GDS to scan, from smallest value to
        largest.
    gds_y : Tuple[float, float], optional
        The y-coordinate span of the GDS to scan, from smallest value to
        largest.
    stage_center : Tuple[float, float], optional
        The (x, y) center of the scan, in motor units.
    gds_center : Tuple[float, float], optional
        The (x, y) center of the scan, in GDS coordinates.
    span : float, optional
        The width of the scan. Units are derived from context; if 
        ``stage_center`` is defined, this is in motor units. If ``gds_center`` 
        is defined, this is in GDS coordinates. If neither is defined, then 
        this is in motor units. The span is from the center +/- span/2.
    span_x : float, optional
        The width of the scan in the x-direction. Units are derived from
        context; if ``stage_center`` is defined, this is in motor units. If
        ``gds_center`` is defined, this is in GDS coordinates. If neither is
        defined, then this is in motor units. The span is from the center
        +/- span_x/2.
    span_y : float, optional
        The width of the scan in the y-direction. Units are derived from
        context; if ``stage_center`` is defined, this is in motor units. If
        ``gds_center`` is defined, this is in GDS coordinates. If neither is
        defined, then this is in motor units. The span is from the center
        +/- span_y/2.
    step_size : float
        Jog step size motors will use when iterating through the box. Units
        are derived from context; if stage_center is defined, this is in motor
        units. If gds_center is defined, this is in GDS coordinates. If set,
        step_size is equal for both x and y axes.
    step_size_x : float, optional
        Jog step size motors will use when iterating through the box. Units
        are derived from context; if stage_center is defined, this is in motor
        units. If gds_center is defined, this is in GDS coordinates. Use this
        parameter to set a different step size for the x-axis.
    step_size_y : float, optional
        Jog step size motors will use when iterating through the box. Units
        are derived from context; if stage_center is defined, this is in motor
        units. If gds_center is defined, this is in GDS coordinates. Use this
        parameter to set a different step size for the y-axis.
    plot : bool, optional
        If a windowed plot is generated displaying data returned from scan.
        If True, matplotlib will be used to generate and open the plot (default
        False).
    settle : float, optional
        Amount of time in seconds the motors will pause in between move 
        commands to allow for settling time (lets vibration/residual motion 
        die out) and improve data reliability (default 0.2).
    go_to_max : bool, optional
        If True, the motors will be moved to the maximum position before
        returning (default True).

    Returns
    -------
    value, position : float, Tuple[float, float]
        The value of the data acquisition unit at the position of the highest
        reading, and the position of that reading in the coordinate system
        defined by the context.
    """
    # Determine bounds of scan region
    if stage_x is not None and stage_y is not None:
        x0, x1 = stage_x
        y0, y1 = stage_y
        COORDS = 'stage'
    elif gds_x is not None and gds_y is not None:
        x0, x1 = gds_x
        y0, y1 = gds_y
        COORDS = 'gds'
    elif stage_center is not None and span is not None:
        x0, x1 = stage_center[0] - span/2, stage_center[0] + span/2
        y0, y1 = stage_center[1] - span/2, stage_center[1] + span/2
        COORDS = 'stage'
    elif gds_center is not None and span is not None:
        x0, x1 = gds_center[0] - span/2, gds_center[0] + span/2
        y0, y1 = gds_center[1] - span/2, gds_center[1] + span/2
        COORDS = 'gds'
    elif span is not None:
        x, y = stage.x.get_position(), stage.y.get_position()
        x0, x1 = x - span/2, x + span/2
        y0, y1 = y - span/2, y + span/2
        COORDS = 'stage'
    elif span_x is not None and span_y is not None:
        x, y = stage.x.get_position(), stage.y.get_position()
        x0, x1 = x - span_x/2, x + span_x/2
        y0, y1 = y - span_y/2, y + span_y/2
        COORDS = 'stage'
    else:
        raise ValueError("Invalid scan parameters")

    # step_size is a required parameter
    if step_size is not None:
        step_size_x = step_size_y = step_size
    elif step_size_x is None or step_size_y is None:
        raise ValueError("'step_size' must be specified")

    # Determine if we're using stage coordinates or GDS coordinates
    if COORDS == 'stage':
        set_position_function = stage.set_position
    elif COORDS == 'gds':
        set_position_function = stage.set_position_gds
    else:
        raise RuntimeError("Congratulations! This error should never happen, notify the developer.")

    # Create map of positions to test
    x = np.arange(x0, x1 + step_size_x, step_size_x)
    y = np.arange(y0, y1 + step_size_y, step_size_y)

    rows, cols = len(x), len(y)
    data = np.zeros((rows, cols))

    if plot:
        fig, ax = plt.subplots(1, 1)
        im = ax.imshow(data, cmap="hot")

    for i in range(rows):
        for j in range(cols):
            set_position_function(x=float(x[i]), y=float(y[i]))
            time.sleep(settle)
            
            data[i, j] = daq.measure()

            if plot:
                im.set_data(data)
                im.set_clim(data.min(), data.max())
                fig.canvas.draw_idle()
                plt.pause(0.000001)

    # Get max value and position
    max_idx = np.unravel_index(np.argmax(data), data.shape)
    max_data = data[max_idx]
    max_x, max_y = x[max_idx[0]], y[max_idx[1]]

    # Move to max position
    if go_to_max:
        set_position_function(x=float(max_x), y=float(max_y))
        time.sleep(settle)

    if plot:
        plt.show()

    return max_data, (max_x, max_y)


def line_scan(
    stage: Stage,
    daq: DataAcquisitionUnitBase,
    axis: str,
    start: float,
    step_size: float = 0.0005,
    settle: float = 0.2,
    iterations: int = 15,
) -> float:
    """
    Performs a line scan of the specified axis.

    You should only employ a linear scan if you're already picking up light,
    as it is intended to take very small steps and will therefore be very slow. 
    Additionally, it will automatically terminate the scan if it goes 
    ``iterations`` steps without finding a new maximum. This is intended to
    stop scanning if you're starting to leave the area of interest.

    Parameters
    ----------
    stage : Stage
        The stage to move.
    daq : DataAcquisitionUnitBase
        The data acquisition unit to use.
    axis : str
        The axis to move. Must be one of 'x', 'y', or 'z'.
    start : float
        The starting position of the scan.
    step_size : float, optional
        The step size of the scan (default 0.0005 microns).
    settle : float, optional
        The time to wait after each move in seconds before taking a reading
        (default 0.2).
    iterations : int, optional
        The number of moves to take without finding a new maximum before
        terminating the scan (default 15).

    Returns
    -------
    max_loc : float
        The location of the maximum in the motor's units.
    """
    if axis in ["x", "y", "z"]:
        motor = getattr(stage, axis)
    motor.move_to(start)
    max_data = daq.measure()
    max_loc = motor.get_position()
    count = 0
    while count < iterations:
        motor.move_by(step_size)
        time.sleep(settle)
        data = daq.measure()
        if data > max_data:
            max_data = data
            max_loc = motor.get_position()
            count = 0
        else:
            count += 1
    return max_loc


def auto_scan(
    stage: Stage,
    daq: DataAcquisitionUnitBase,
    stage_x: Tuple[float, float] = None,
    stage_y: Tuple[float, float] = None,
    gds_x: Tuple[float, float] = None,
    gds_y: Tuple[float, float] = None,
    stage_center: Tuple[float, float] = None,
    gds_center: Tuple[float, float] = None,
    span: float = 0.025,
    step_size: float = 0.005,
    step_size_x: float = None,
    step_size_y: float = None,
    settle: float = 0.2,
    go_to_max: bool = True,
) -> Tuple[float, float]:
    """
    Performs a box scan of given dimensions and then refines the scan around the peak.

    You must specify one of the following sets of parameters: 
    * ``stage_x`` and ``stage_y``
    * ``gds_x`` and ``gds_y``
    * ``stage_center`` and ``span``
    * ``gds_center`` and ``span``
    * ``span`` (with center not specified, centers assumes current location)

    Additionally, you must specify one of the following parameter sets:
    * ``step_size``
    * ``step_size_x`` and ``step_size_y``

    Parameters
    ----------
    stage : Stage
        The stage object that provides access to the hardware.
    daq : DataAcquisitionUnitBase
        The preconfigured data acquisition unit to use for taking measurements.
        This function repeatedly calls the 
        :py:func:`DataAcquisitionUnitBase.measure` method to acquire scan data.
    stage_x : Tuple[float, float], optional
        The x-coordinate span of the stage to scan, in motor units, from 
        smallest value to largest.
    stage_y : Tuple[float, float], optional
        The y-coordinate span of the stage to scan, in motor units, from 
        smallest value to largest.
    gds_x : Tuple[float, float], optional
        The x-coordinate span of the GDS to scan, from smallest value to
        largest.
    gds_y : Tuple[float, float], optional
        The y-coordinate span of the GDS to scan, from smallest value to
        largest.
    stage_center : Tuple[float, float], optional
        The (x, y) center of the scan, in motor units.
    gds_center : Tuple[float, float], optional
        The (x, y) center of the scan, in GDS coordinates.
    span : float, optional
        The width of the scan. Units are derived from context; if 
        ``stage_center`` is defined, this is in motor units. If ``gds_center`` 
        is defined, this is in GDS coordinates. If neither is defined, then 
        this is in motor units. The span is from the center +/- span/2.
    step_size : float
        Jog step size motors will use when iterating through the box. Units
        are derived from context; if stage_center is defined, this is in motor
        units. If gds_center is defined, this is in GDS coordinates. If set,
        step_size is equal for both x and y axes.
    step_size_x : float, optional
        Jog step size motors will use when iterating through the box. Units
        are derived from context; if stage_center is defined, this is in motor
        units. If gds_center is defined, this is in GDS coordinates. Use this
        parameter to set a different step size for the x-axis.
    step_size_y : float, optional
        Jog step size motors will use when iterating through the box. Units
        are derived from context; if stage_center is defined, this is in motor
        units. If gds_center is defined, this is in GDS coordinates. Use this
        parameter to set a different step size for the y-axis.
    settle : float, optional
        Amount of time in seconds the motors will pause in between move 
        commands to allow for settling time (lets vibration/residual motion 
        die out) and improve data reliability (default 0.2).
    go_to_max : bool, optional
        If True, the motors will be moved to the maximum position before
        returning (default True).

    Returns
    -------
    position : Tuple[float, float]
        The position of the highest reading in the motor coordinate system.
    """
    value, position = basic_scan(
        stage=stage,
        daq=daq,
        stage_x=stage_x,
        stage_y=stage_y,
        gds_x=gds_x,
        gds_y=gds_y,
        stage_center=stage_center,
        gds_center=gds_center,
        span=span,
        step_size=step_size,
        step_size_x=step_size_x,
        step_size_y=step_size_y,
        settle=settle,
    )

    log.info(f"Max data '{value}' found at {position}")

    # Fine tune max position
    SEARCH_AREA = 0.05
    FINE_STEP = 0.0005
    x_max = line_scan(stage, daq, "x", position[0] - SEARCH_AREA / 2, step_size=FINE_STEP)
    y_max = line_scan(stage, daq, "y", position[1] - SEARCH_AREA / 2, step_size=FINE_STEP)

    if go_to_max:
        stage.set_position(x=x_max, y=y_max)

    log.info(f"Fine-tuned max data location: {(x_max, y_max)}")
    return (x_max, y_max)
