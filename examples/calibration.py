# -*- coding: utf-8 -*-
#
# Copyright © Autogator Project Contributors
# Licensed under the terms of the GPLv3+ License
# (see autogator/__init__.py for details)

"""
# Calibration

Calibrates the stage so that circuits can be accessed by GDS coordinate
instead of motor coordinates.

Ordinarily, you would save the calibration matrix to a file, or associate
it with a setup. This example simply prints the calibration matrix to the
screen.
"""

from autogator.api import load_default_configuration
from autogator.circuit import CircuitMap
from autogator.controllers import KeyboardControl, KeyloopKeyboardBindings
from autogator.routines import auto_scan, calibrate


def scope_configure_single_meas():
    """
    Configure the Rohde & Schwarz oscilloscope for single-shot measurements.

    We use the API defined in PyroLab
    (https://pyrolab.readthedocs.io/en/latest/) which is wrapped in 
    ``autogator.hardware``. Because it implements
    ``autogator.hardware.DataAcquisitionUnitBase``, it provides a ``measure()``
    method that can is used to detect intensity at each measurement point.

    In this example, we use channel 1 for our signal.
    """
    oscope = stage.scope.driver

    # Scope setup parameters
    CHANNEL = 1
    RANGE = 0.6
    COUPLING = "DCLimit"
    POSITION = -2.0

    oscope.set_channel(CHANNEL, range=RANGE, coupling=COUPLING, position=POSITION)
    oscope.set_auto_measurement(source=F"C{CHANNEL}W1")
    oscope.wait_for_device()


def laser_configure():
    """
    Configure the laser for what we believe will be the maximum signal, 1550 nm.

    In this example, we are using the Santec TSL-550 laser as implemented by
    PyroLab.
    """
    laser = stage.laser
    laser.on()
    laser.power(-4.0)
    laser.wavelength(1550.0)


def keyboard_control(stage):
    """
    Default keyboard control loop for manual motion.
    """
    kc = KeyboardControl(stage, KeyloopKeyboardBindings())
    kc.loop()


def auto_calibration_callback(stage, daq, circuit, controller) -> None:
    """
    Moves to the specified circuit and optimizes alignment.

    ``calibrate()`` requires a callback function that takes the stage,
    DAQ, circuit, and controller as arguments.

    We use this callback to move to the next location and optimize the
    alignment. We have roughly found where the light is at each location,
    so this function automatically moves to the next location and 
    optimizes the alignment. If it fails, it then allows you to manually
    move the stage before it attempts to optimize again.

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
    SCAN_SPAN = 0.035
    SCAN_STEP = 0.0024

    next_pos = next(locs)

    first = True
    while True:
        if first:
            stage.set_position(pos=next_pos)
            first = False

        auto_scan(stage=stage, daq=daq, span=SCAN_SPAN, step_size=SCAN_STEP, plot=True)
        
        scan_again = input("Manually move to new location and scan again? (y/n) [Enter]: ")
        if scan_again == 'y':
            keyboard_control()
        else:
            break
    print("Exiting callback")


def next_loc():
    """
    Generator function. Yields the next location in the list of locations.

    This function is used by ``auto_calibration_callback()`` to move to the
    next location in the list of locations. These locations are roughly
    the stage positions where we'll find light (this will be different
    almost every time you swap out a chip or change setups, so update these
    values accordingly).

    These locations should correspond, in the same order, to the calibration
    functions as found in the CircuitMap.

    Returns
    -------
    next_pos : float
        The next location in the list of locations.
    """
    yield from [
        [9.9237, 11.5935, None, None, None, 100.0],
        [10.0975, 3.3209, None, None, None, 100.0],
        [1.1629, 3.1288, None, None, None, 100.0],
    ]


if __name__ == "__main__":
    cmap = CircuitMap.loadtxt("data/circuitmap.txt")
    calib = cmap.filterby(calibration_circuit="True")

    stage = load_default_configuration().get_stage()

    scope_configure_single_meas()
    laser_configure()

    locs = next_loc()

    matrix = calibrate(stage=stage, daq=stage.scope, circuits=calib, callback=auto_calibration_callback)
    print("Calibration matrix:")
    print(matrix)
