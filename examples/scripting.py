# -*- coding: utf-8 -*-
#
# Copyright © Autogator Project Contributors
# Licensed under the terms of the MIT License
# (see autogator/__init__.py for details)

"""
Motion
------

Motion example. Uses the default keyboard controller and default keybindings.
"""

import json

from autogator.hardware import HardwareConfiguration, StageConfiguration
from autogator.routines import KeyboardControl, KeyloopKeyboardBindings, basic_scan


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
jarvis = HardwareConfiguration(
    classname="",
    parameters={
        "pyroname": "asgard.jarvis",
        "ns_host": "camacholab.ee.byu.edu",
    }
)

sc = StageConfiguration(
    x=captainamerica,
    y=hulk,
    psi=wolverine,
    auxiliaries={
        "laser": wanda,
        "scope": dormammu,
        "lamp": jarvis,
    }
)


stage = sc.get_stage()


def hardware_config_json():
    scj = sc.json()
    parsed = json.loads(scj)
    print(json.dumps(parsed, indent=4))


def keyboard_control():
    kc = KeyboardControl(stage, KeyloopKeyboardBindings())
    kc.loop()


def scope_configure_single_meas():
    oscope = stage.scope.driver

    # Scope setup
    CHANNEL = 1
    RANGE = 0.4
    COUPLING = "DCLimit"
    POSITION = -5.0

    oscope.set_channel(CHANNEL, range=RANGE, coupling=COUPLING, position=POSITION)
    oscope.set_auto_measurement(source=F"C{CHANNEL}W1")
    oscope.wait_for_device()


def my_basic_scan():
    basic_scan(stage, stage.scope, (8, 12), (4, 8), step_size=1, plot=True, go_to_max=False)
