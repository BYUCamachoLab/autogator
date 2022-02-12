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

import json

import numpy as np

from autogator.api import save_default_configuration, load_default_configuration
from autogator.hardware import HardwareConfiguration, StageConfiguration
from autogator.profiles import update_calibration_matrix


captainamerica = HardwareConfiguration(
    classname="Z825BLinearStage",
    parameters={
        "pyroname": "asgard.captainamerica",
        "ns_host": "camacholab.ee.byu.edu",
    }
)
hulk = HardwareConfiguration(
    classname="Z825BLinearStage",
    parameters={
        "pyroname": "asgard.hulk",
        "ns_host": "camacholab.ee.byu.edu",
    }
)
wolverine = HardwareConfiguration(
    classname="PRM1Z8RotationalStage",
    parameters={
        "pyroname": "asgard.wolverine",
        "ns_host": "camacholab.ee.byu.edu",
    }
)
dormammu = HardwareConfiguration(
    classname="RohdeSchwarzOscilliscope",
    parameters={
        "name": "dormammu",
        "address": "10.32.112.162",
    }
)
wanda = HardwareConfiguration(
    classname="TSL550Laser",
    parameters={
        "pyroname": "westview.scarletwitch",
        "ns_host": "camacholab.ee.byu.edu",
    }
)
# jarvis = HardwareConfiguration(
#     classname="",
#     parameters={
#         "pyroname": "asgard.jarvis",
#         "ns_host": "camacholab.ee.byu.edu",
#     }
# )

sc = StageConfiguration(
    x=captainamerica,
    y=hulk,
    psi=wolverine,
    auxiliaries={
        "laser": wanda,
        "scope": dormammu,
        # "lamp": jarvis,
    },
    calibration_matrix="./data/calib_mat.txt",
)


def hardware_config_json():
    scj = sc.json()
    parsed = json.loads(scj)
    print(json.dumps(parsed, indent=4))


if __name__ == "__main__":
    hardware_config_json()
    save_default_configuration("asgard", sc)
    matrix = np.loadtxt("data/calib_mat.txt")
    update_calibration_matrix("asgard", matrix)
