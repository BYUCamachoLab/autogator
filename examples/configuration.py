# -*- coding: utf-8 -*-
#
# Copyright © Autogator Project Contributors
# Licensed under the terms of the GNU GPLv3+ License
# (see autogator/__init__.py for details)

"""
# Configuration

Configuration example. Sets the network hardware names and parameters and
persists them as the default configuration.
"""

import numpy as np

from autogator.api import save_default_configuration
from autogator.hardware import HardwareConfiguration, StageConfiguration
from autogator.profiles import update_calibration_matrix


x = HardwareConfiguration(
    classname="Z825BLinearStage",
    parameters={
        "pyroname": "x",
        "ns_host": "yourdomain.com",
    }
)
y = HardwareConfiguration(
    classname="Z825BLinearStage",
    parameters={
        "pyroname": "y",
        "ns_host": "yourdomain.com",
    }
)
scope = HardwareConfiguration(
    classname="RohdeSchwarzOscilliscope",
    parameters={
        "name": "scope",
        "address": "1.2.3.4",
    }
)
laser = HardwareConfiguration(
    classname="TSL550Laser",
    parameters={
        "pyroname": "laser",
        "ns_host": "yourdomain.com",
    }
)

sc = StageConfiguration(
    x=x,
    y=y,
    auxiliaries={
        "laser": laser,
        "scope": scope,
    },
    calibration_matrix="./data/calib_mat.txt",
)


if __name__ == "__main__":
    save_default_configuration("myprofile", sc)
    matrix = np.loadtxt("data/calib_mat.txt")
    update_calibration_matrix("myprofile", matrix)
