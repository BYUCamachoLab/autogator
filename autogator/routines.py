# -*- coding: utf-8 -*-
#
# Copyright © Autogator Project Contributors
# Licensed under the terms of the GNU GPLv3+ License
# (see autogator/__init__.py for details)

"""
# Routines

A set of common, useful stage operations implemented using common calls from 
abstracted motors and auxiliary devices. In theory, setups utilizing different
hardware should be able to use the same routines without any modification.

Using this module, you can

* define routines that take advantage of abstracted objects like a "stage" or
  a "data acquisition unit".
* reuse routines even with different hardware, given they implement the 
  interfaces defined in autogator.hardware

It is easy to write your own routines that will work regardless of the hardware
available. This makes them reusable between different setups. Routines are
written to be functional, rather than object oriented. They usually accept
as parameters preconfigured classes with a known API, such as a Stage, a Laser,
or a DataAcquisitionUnitBase. The routine doesn't do any configuration on such
objects; they should be passed in preconfigured.
"""

import logging
import time
from typing import Callable, List, Tuple

import numpy as np
import matplotlib.pyplot as plt

from autogator.circuits import Circuit
from autogator.hardware import DataAcquisitionUnitBase, Stage
from autogator.controllers import KeyboardControl


log = logging.getLogger(__name__)


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
    stage : Stage
        The stage to move.
    daq : DataAcquisitionUnitBase
        The DAQ to use for data acquisition.
    circuit : Circuit
        The circuit being moved to for calibration.
    controller : KeyboardControl
        The controller to use for control input.
    """
    print(f"Center {circuit} in view, then quit the controller.")
    controller.loop()

    SCAN_SPAN = 0.025
    SCAN_STEP = 0.005

    print("Optimizing alignment...")
    do_scan = True
    while do_scan:
        auto_scan(stage, daq, SCAN_SPAN, SCAN_STEP)
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
        - circuit: The circuit currently being referenced for calibration.
        - controller: The controller to use for control input.

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

    calibration_matrix = np.array(
        [
            [a[0][0], a[1][0], a[2][0]], 
            [a[3][0], a[4][0], a[5][0]], 
            [      0,       0,       1],
        ]
    )

    return calibration_matrix


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
        jog_position_function = stage.jog_position
    elif COORDS == 'gds':
        set_position_function = stage.set_position_gds
        jog_position_function = stage.jog_position_gds
    else:
        raise RuntimeError("Congratulations! This error should never happen, notify the developer.")

    # Create map of positions to test
    x = np.arange(x0, x1 + step_size_x, step_size_x)
    y = np.arange(y0, y1 + step_size_y, step_size_y)

    log.debug(f"Current position: ({stage.x.get_position()}, {stage.y.get_position()})")
    log.debug(f"Scan range (x): {x[0]} - {x[-1]}")
    log.debug(f"Scan range (y): {y[0]} - {y[-1]}")

    rows, cols = len(x), len(y)
    data = np.zeros((rows, cols))
    pos = []

    if plot:
        fig, ax = plt.subplots(1, 1, num="Basic Scan")
        im = ax.imshow(data, cmap="hot", extent=(x0, x1, y0, y1))
        cbar = fig.colorbar(im, ax=ax)

    set_position_function(x=float(x[0]), y=float(y[0]))
    try:
        for i in range(rows):
            for j in range(cols):
                time.sleep(settle)

                data[i, j] = daq.measure()
                loc = i * rows + j + 1
                if loc < rows * cols:
                    data.flat[i * rows + j + 1] = np.max(data) * 0.9

                if plot:
                    im.set_data(data)
                    im.autoscale()
                    fig.canvas.draw_idle()
                    plt.pause(0.001)

                pos.append((stage.get_position()[0], stage.get_position()[1]))

                jog_position_function(y=step_size_y)

            set_position_function(y=float(y[0]))
            jog_position_function(x=step_size_x)
    except KeyboardInterrupt:
        pass

    # Get max value and position
    max_idx = np.argmax(data)
    max_coord = np.unravel_index(max_idx, data.shape)
    max_data = data[max_coord]
    max_x, max_y = pos[max_idx]

    # Move to max position
    set_position_function(x=float(max_x), y=float(max_y))

    if plot:
        plt.show()
        print("Close the plot window to continue...")

    return max_data, (max_x, max_y)


def line_scan(
    stage: Stage,
    daq: DataAcquisitionUnitBase,
    axis: str,
    start: float,
    step_size: float = 0.0005,
    settle: float = 0.2,
    iterations: int = 15,
    plot: bool = False,
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
    plot : bool, optional
        Whether to plot the data (default False).

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

    if plot:
        fig, ax = plt.subplots(1, 1, num=f"{axis} Line Scan")
        line, = ax.plot([], [])
        fig.canvas.draw()

    pos = []
    vals = []
    trend = 0

    while count < iterations and (trend < (0.1 * max(vals) if vals else 0)):
        motor.move_by(step_size)
        time.sleep(settle)
        data = daq.measure()

        pos.append(motor.get_position())
        vals.append(data)
        
        if plot:
            line.set_data(pos, vals)
            min_x, max_x = pos[0], pos[-1]
            diff_x = max_x - min_x
            if diff_x != 0:
                ax.set_xlim(min_x - 0.1*diff_x, max_x + 0.1*diff_x)
            min_y, max_y = min(vals), max(vals)
            diff_y = max_y - min_y
            if diff_y != 0:
                ax.set_ylim(min_y - 0.1*diff_y, max_y + 0.1*diff_y)
            fig.canvas.draw_idle()
            plt.pause(0.001)

        if data > max_data:
            max_data = data
            max_loc = motor.get_position()
            count = 0
        elif data == max_data:
            count = 0
        else:
            count += 1

        if len(vals) > 5:
            trend = sum(np.diff(vals[-5:]))

    if plot:
        plt.show()
        print("Close the plot window to continue...")

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
    span: float = 0.06,
    step_size: float = 0.005,
    step_size_x: float = None,
    step_size_y: float = None,
    plot=False,
    settle: float = 0.2,
) -> Tuple[float, float]:
    """
    Performs a box scan of given dimensions and then refines the scan around the peak.

    The stage always moves to the max position upon completion of this function.

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
    plot : bool, optional
        Whether to plot the scan data (default False).
    settle : float, optional
        Amount of time in seconds the motors will pause in between move 
        commands to allow for settling time (lets vibration/residual motion 
        die out) and improve data reliability (default 0.2).

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
        plot=plot,
        settle=settle,
    )

    log.info(f"Coarse max value '{value}' found at {position}")

    # Fine tune max position
    SEARCH_AREA = 0.025
    FINE_STEP = 0.0005
    x_max = line_scan(stage, daq, "x", position[0] - SEARCH_AREA / 2, step_size=FINE_STEP, plot=plot)
    stage.set_position(x=x_max)
    y_max = line_scan(stage, daq, "y", position[1] - SEARCH_AREA / 2, step_size=FINE_STEP, plot=plot)
    stage.set_position(y=y_max)

    value = daq.measure()
    log.info(f"Fine max value '{value}' found at {position}")

    return (x_max, y_max)
