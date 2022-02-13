# -*- coding: utf-8 -*-
#
# Copyright © Autogator Project Contributors
# Licensed under the terms of the GNU GPLv3+ License
# (see autogator/__init__.py for details)

"""
# API

The following functions can be conveniently imported directly from
``autogator.api``:

## Hardware Profiles

* [`load_configuration()`][autogator.profiles.load_configuration]
* [`save_configuration()`][autogator.profiles.save_configuration]
* [`load_default_configuration()`][autogator.profiles.load_default_configuration]
* [`save_default_configuration()`][autogator.profiles.save_default_configuration]
* [`update_calibration_matrix()`][autogator.profiles.update_calibration_matrix]

## Experiments and Runners

* [`Circuit`][autogator.circuits.Circuit]
* [`CircuitMap`][autogator.circuits.CircuitMap]
* [`Experiment`][autogator.experiments.Experiment]
* [`ExperimentRunner`][autogator.experiments.ExperimentRunner]

## Configuration Objects

* [`HardwareConfiguration`][autogator.hardware.HardwareConfiguration]
* [`StageConfiguration`][autogator.hardware.StageConfiguration]

"""

from autogator import AUTOGATOR_DATA_DIR, AUTOGATOR_CONFIG_DIR
from autogator.experiments import Experiment, ExperimentRunner
from autogator.hardware import (
    HardwareConfiguration, 
    StageConfiguration, 
)
from autogator.profiles import (
    load_configuration,
    save_configuration,
    update_calibration_matrix,
    load_default_configuration,
    save_default_configuration,
)


__all__ = [
    "HardwareConfiguration",
    "StageConfiguration",
    "load_configuration",
    "save_configuration",
    "load_default_configuration",
    "save_default_configuration",
    "update_calibration_matrix",
    "Experiment",
    "ExperimentRunner",
]
