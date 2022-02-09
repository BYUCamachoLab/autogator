# -*- coding: utf-8 -*-
#
# Copyright © Autogator Project Contributors
# Licensed under the terms of the GNU GPLv3+ License
# (see autogator/__init__.py for details)

"""
# API

A series of convenience functions.
"""

import pathlib
import shutil
from typing import Union

import numpy as np

from autogator import AUTOGATOR_DATA_DIR, AUTOGATOR_CONFIG_DIR
from autogator.experiment import Experiment
from autogator.hardware import (
    HardwareConfiguration, 
    StageConfiguration, 
    _CALIBRATION_PARAM_FILE, 
    _DEFAULT_STAGE_CONFIGURATION,
)


def set_calibration_matrix(filename: Union[str, pathlib.Path]):
    """
    Set the calibration matrix for the stage.

    Parameters
    ----------
    filename : str or pathlib.Path
        The filename of the calibration matrix to use.
    """
    if isinstance(filename, str):
        filename = pathlib.Path(filename)
    if not filename.is_file():
        raise ValueError("Calibration matrix file not found.")
    shutil.copyfile(filename, _CALIBRATION_PARAM_FILE)


def get_calibration_matrix() -> np.ndarray:
    """
    Get the calibration matrix for the stage.

    Returns
    -------
    np.ndarray
        The most recent calibration matrix, if it exists, else None.
    """
    return np.loadtxt(_CALIBRATION_PARAM_FILE) if _CALIBRATION_PARAM_FILE.is_file() else None


def invalidate_calibration_matrix() -> None:
    """
    Invalidates the default calibration matrix for the stage.
    """
    if _CALIBRATION_PARAM_FILE.is_file():
        _CALIBRATION_PARAM_FILE.unlink()
    

def load_default_configuration() -> StageConfiguration:
    """
    Loads the default stage configuration.

    Returns
    -------
    StageConfiguration
        The default stage configuration.
    """
    if not _DEFAULT_STAGE_CONFIGURATION.is_file():
        raise ValueError("Default stage configuration not configured.")
    return StageConfiguration.parse_file(_DEFAULT_STAGE_CONFIGURATION)


def save_default_configuration(config: StageConfiguration) -> None:
    """
    Saves the default stage configuration.

    Parameters
    ----------
    config : StageConfiguration
        The stage configuration to save.
    """
    with _DEFAULT_STAGE_CONFIGURATION.open("w") as f:
        f.write(config.json())
