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
    load_default_configuration,
    save_default_configuration,
)


__all__ = [
    "HardwareConfiguration",
    "StageConfiguration",
    "load_default_configuration",
    "save_default_configuration",
    "Experiment",
    "ExperimentRunner",
]    
