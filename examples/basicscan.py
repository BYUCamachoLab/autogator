# -*- coding: utf-8 -*-
#
# Copyright © Autogator Project Contributors
# Licensed under the terms of the MIT License
# (see autogator/__init__.py for details)

"""
Basic Scan
----------

Basic scan example. Allows you to adjust the location of the stage and then
performs a basic scan about the location you stop at.

In this example, your stage configuration must include a "daq" object
configuration as an auxiliary for the stage.
"""

from autogator.hardware import StageConfiguration
from autogator.routines import KeyboardControl, KeyloopKeyboardBindings, basic_scan


cfg = StageConfiguration.parse_file("stage_config.json")
stage = cfg.get_stage()

# Distances in mm for our hardware...
sweep_distance_x = 0.5
sweep_distance_y = 0.1
step_size_x = 0.05
step_size_y = 0.01

kc = KeyboardControl(stage, KeyloopKeyboardBindings())
kc.loop()

basic_scan(
    stage, 
    stage.daq, 
    span_x = sweep_distance_x, 
    span_y = sweep_distance_y, 
    step_size_x = step_size_x, 
    step_size_y = step_size_y,
    plot=True,
    go_to_max=True,
)
