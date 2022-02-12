# -*- coding: utf-8 -*-
#
# Copyright © Autogator Project Contributors
# Licensed under the terms of the GNU GPLv3+ License
# (see autogator/__init__.py for details)

"""
# API

A series of convenience functions.
"""

from autogator import AUTOGATOR_DATA_DIR, AUTOGATOR_CONFIG_DIR
from autogator.experiment import Experiment, ExperimentRunner
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
