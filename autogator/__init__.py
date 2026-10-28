# -*- coding: utf-8 -*-
# Copyright © 2019- AutoGator Project Contributors and others (see AUTHORS.txt).
# The resources, libraries, and some source files under other terms.
#
# This file is part of AutoGator.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
# AutoGator

A software package for camera-assisted motion control of PIC chip interrogation
platforms.
"""

import os
import pathlib
import platform
import sys
from datetime import date
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _version

if sys.version_info < (3, 11, 0):
    raise Exception(
        "autogator requires Python 3.11+ (version "
        + platform.python_version()
        + " detected)."
    )

# Imported after the version guard so that an unsupported interpreter reports
# the message above rather than failing on a dependency import first.
from .circuits import CircuitMap

__author__ = "CamachoLab"
__copyright__ = "Copyright 2022, CamachoLab"
try:
    # The version is declared once, in pyproject.toml; read it back from the
    # installed distribution metadata rather than duplicating it here.
    __version__ = _version("AutoGator")
except PackageNotFoundError:  # not installed, e.g. a bare source checkout
    __version__ = "0.0.0.dev0"
__license__ = "GPLv3+"
__maintainer__ = "Sequoia Ploeg"
__maintainer_email__ = "sequoia.ploeg@byu.edu"
__status__ = "Development"  # "Production"
__project_url__ = "https://github.com/BYUCamachoLab/autogator"
__forum_url__ = "https://github.com/BYUCamachoLab/autogator/issues"
__website_url__ = "https://camacholab.byu.edu/"


import warnings
warnings.filterwarnings("default", category=DeprecationWarning)

from appdirs import AppDirs

# Name the data directory explicitly. It used to be derived from a __name__
# override, which broke submodule imports; keep the old name so existing
# profiles and configuration are still found.
_dirs = AppDirs("AutoGator", __author__)
AUTOGATOR_DATA_DIR = pathlib.Path(_dirs.user_data_dir)
AUTOGATOR_DATA_DIR.mkdir(parents=True, exist_ok=True)

AUTOGATOR_CONFIG_DIR = AUTOGATOR_DATA_DIR / "config"
AUTOGATOR_CONFIG_DIR.mkdir(parents=True, exist_ok=True)

print("Welcome to AutoGator!")
print("© 2019-{}, CamachoLab".format(date.today().year))

import logging
import logging.handlers


def get_loglevel() -> int:
    loglevel = os.getenv("AUTOGATOR_LOGLEVEL", "INFO")
    try:
        loglevel = getattr(logging, loglevel.upper())
    except AttributeError:
        loglevel = logging.INFO
    return loglevel


AUTOGATOR_LOGFILE = AUTOGATOR_DATA_DIR / "autogator.log"
logfile = os.getenv("AUTOGATOR_LOGFILE", AUTOGATOR_LOGFILE)

# Configure only the "autogator" logger, and only if the application has not
# already set up logging itself; a library must not configure the root logger.
if len(logging.root.handlers) == 0:
    _log = logging.getLogger(__name__)
    f = logging.Formatter('%(asctime)s.%(msecs)03d %(process)-5s %(processName)-10s %(name)-12s %(levelname)-8s %(message)s', datefmt="%Y-%m-%d %H:%M:%S")

    h = logging.handlers.RotatingFileHandler(logfile, 'a', 30000, 10)
    h.setFormatter(f)
    _log.addHandler(h)

    h = logging.StreamHandler()
    h.setFormatter(f)
    _log.addHandler(h)

    _log.setLevel(get_loglevel())
    _log.debug("Autogator logging configured")
