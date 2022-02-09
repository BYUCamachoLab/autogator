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

A software package for camera-assisted motion control of PIC chip interrogation platforms.
"""

import pathlib
import platform
import sys
from datetime import date

if sys.version_info < (3, 7, 0):
    raise Exception(
        "autogator requires Python 3.7+ (version "
        + platform.python_version()
        + " detected)."
    )

__name__ = "AutoGator"
__author__ = "CamachoLab"
__copyright__ = "Copyright 2022, CamachoLab"
__version__ = "0.2.0dev0"
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

_dirs = AppDirs(__name__, __author__)
AUTOGATOR_DATA_DIR = pathlib.Path(_dirs.user_data_dir)
AUTOGATOR_DATA_DIR.mkdir(parents=True, exist_ok=True)

AUTOGATOR_CONFIG_DIR = AUTOGATOR_DATA_DIR / "config"
AUTOGATOR_CONFIG_DIR.mkdir(parents=True, exist_ok=True)

print("Welcome to AutoGator!")
print("© 2019-{}, CamachoLab".format(date.today().year))

import logging
logging.basicConfig(
    level=logging.INFO,
)
