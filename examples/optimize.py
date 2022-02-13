# -*- coding: utf-8 -*-
#
# Copyright © Autogator Project Contributors
# Licensed under the terms of the GPLv3+ License
# (see autogator/__init__.py for details)

"""
# Optimizer

Optimization example. Allows you to first navigate the stage to the vicinity
of a circuit to test, and then does a coarse scan to try to locate some
signal. Once a signal has been found, switches to a fine "line scan" that
goes to the general location the signal was found in, switches to a fine step,
and maximizes the x and y return. If optimization is unsuccessful, allows you
to relocate the chip and try again.

In this example, your stage configuration must include a data acquisition
object configuration as an auxiliary device for the stage. We use a
Rohde & Schwarz oscilloscope as our data acquisition unit. See the function
docstrings below for more details.
"""

from autogator.api import load_default_configuration
from autogator.controllers import KeyboardControl, KeyloopKeyboardBindings
from autogator.routines import auto_scan


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


if __name__ == "__main__":
    stage = load_default_configuration().get_stage()

    scope_configure_single_meas()
    laser_configure()

    SCAN_SPAN = 0.06
    SCAN_STEP = 0.0024

    while True:
        print("Entering keyboard control loop. Move to desired location, then press 'q'.")
        keyboard_control(stage)

        print("Optimizing alignment...")
        auto_scan(stage=stage, daq=stage.scope, span=SCAN_SPAN, step_size=SCAN_STEP, plot=True)

        scan_again = input("Move to new location and scan again? (y/n) [Enter]: ")
        if scan_again == 'y':
            continue
        else:
            break
