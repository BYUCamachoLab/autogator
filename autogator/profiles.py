# -*- coding: utf-8 -*-
#
# Copyright © Autogator Project Contributors
# Licensed under the terms of the GNU GPLv3+ License
# (see autogator/__init__.py for details)

"""
# Profiles

An API that allows for storing and loading default stage configurations.
Useful if you use AutoGator as a client to connect to several different
hardware configurations or setups.

Also provides a way to associate calibration matrices with configurations.
"""

from pathlib import Path
from typing import List

import numpy as np
from pydantic import BaseModel

from autogator import AUTOGATOR_DATA_DIR
from autogator.hardware import StageConfiguration


PROFILES_DIR = AUTOGATOR_DATA_DIR / "profiles"
PROFILES_DIR.mkdir(parents=True, exist_ok=True)
CALIBRATION_DIR = AUTOGATOR_DATA_DIR / "calibration"
CALIBRATION_DIR.mkdir(parents=True, exist_ok=True)

_REGISTRY_FILE = PROFILES_DIR / "_registry.json"


class _ConfigurationRegistry(BaseModel):
    """
    A registry of configurations. AutoGator internal object.

    Acts as a singleton for this module.
    """
    default: str = ""

    def save(self):
        """
        Save the current configuration registry to disk.

        Always saves to the same registry file in the profiles directory.
        """
        with _REGISTRY_FILE.open("w") as f:
            f.write(self.json())


try:
    _cfg_registry = _ConfigurationRegistry.parse_file(_REGISTRY_FILE)
except FileNotFoundError:
    _cfg_registry = _ConfigurationRegistry()
    _cfg_registry.save()


def known_configurations() -> List[str]:
    """
    Returns a list of known hardware configuration profiles.

    Returns
    -------
    List[str]
        A list of known profiles.
    """
    return [
        profile.stem
        for profile in PROFILES_DIR.glob("*.json")
        if not profile.name.startswith("_")
    ]


def update_calibration_matrix(name: str, matrix: np.ndarray) -> None:
    """
    Updates the calibration matrix for a configuration.

    Names cannot begin with an underscore. Calibration matrices can only be
    updated for known configurations (see ``known_configurations``).

    Parameters
    ----------
    name : str
        The name of the profile to associate the calibration matrix with.
    matrix : np.ndarray
        The calibration matrix to save.

    Raises
    ------
    ValueError
        If the name is invalid or the configuration does not exist.
    """
    if name.startswith("_"):
        raise ValueError("Names cannot begin with an underscore.")
    if name not in known_configurations():
        raise ValueError(f"Cannot associate matrix with configuration '{name}', which does not exist.")
    matrix_path = CALIBRATION_DIR / f"{name}.txt"
    np.savetxt(str(matrix_path), matrix)

    cfg = load_configuration(name)
    cfg.calibration_matrix = matrix_path
    update_configuration(name, cfg)


def save_configuration(name: str, configuration: StageConfiguration) -> None:
    """
    Saves a configuration to a file.

    Names cannot begin with an underscore.

    Parameters
    ----------
    name : str
        The name of the configuration profile.
    configuration : StageConfiguration
        The stage configuration to save.

    Raises
    ------
    ValueError
        If the name is invalid or already in use. To overwrite an existing
        profile, use ``update_configuration``.
    """
    if name.startswith("_"):
        raise ValueError("Names cannot begin with an underscore.")
    profile_path = PROFILES_DIR / f"{name}.json"
    if profile_path.is_file():
        raise ValueError(f"Profile '{name}' already exists.")
    configuration.save(profile_path)


def update_configuration(name: str, config: StageConfiguration) -> None:
    """
    Updates the default stage configuration.

    If the name is not in use, it will be saved as a new profile. If the name
    is in use, the configuration will be overwritten. Names cannot begin with
    an underscore.

    Parameters
    ----------
    config : StageConfiguration
        The stage configuration to save.

    Raises
    ------
    ValueError
        If the name is invalid.
    """
    if name.startswith("_"):
        raise ValueError("Names cannot begin with an underscore.")
    profile_path = PROFILES_DIR / f"{name}.json"
    with profile_path.open("w") as f:
        f.write(config.json())


def load_configuration(name: str) -> StageConfiguration:
    """
    Loads a configuration from a file.

    Parameters
    ----------
    name : str
        The name of the profile to load.

    Raises
    ------
    ValueError
        If the profile does not exist.
    """
    profile_path = PROFILES_DIR / f"{name}.json"
    if profile_path.is_file():
        return StageConfiguration.parse_file(profile_path)
    else:
        raise ValueError(f"Profile '{name}' does not exist.")


def delete_configuration(name: str) -> None:
    """
    Deletes a configuration profile and its associated calibration matrix.

    Parameters
    ----------
    name : str
        The name of the profile to delete.

    Raises
    ------
    ValueError
        If the profile does not exist.
    """
    profile_path = PROFILES_DIR / f"{name}.json"
    if profile_path.is_file():
        profile_path.unlink()
    else:
        raise ValueError(f"Profile '{name}' does not exist.")
    calibration_path = CALIBRATION_DIR / f"{name}.txt"
    if calibration_path.is_file():
        calibration_path.unlink()


def load_default_configuration() -> StageConfiguration:
    """
    Loads the default stage configuration.

    Returns
    -------
    StageConfiguration
        The default stage configuration.

    Raises
    ------
    ValueError
        If the default configuration has not been set.
    """
    default = _cfg_registry.default
    if default:
        return load_configuration(default)
    else:
        raise ValueError("Default stage configuration not configured.")


def save_default_configuration(name: str, config: StageConfiguration) -> None:
    """
    Creates a named default stage configuration.

    Requires a name to enforce uniqueness, but can be loaded again without the
    name using ``load_default_configuration``.

    Parameters
    ----------
    name : str
        The name of the configuration profile.
    config : StageConfiguration
        The stage configuration to save.

    Raises
    ------
    ValueError
        If the name is invalid.
    """
    update_configuration(name, config)
    _cfg_registry.default = name
    _cfg_registry.save()
