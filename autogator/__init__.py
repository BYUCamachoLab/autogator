# -*- coding: utf-8 -*-
#
# MIT License
#
# Copyright © 2019-2022 Autogator Project Contributors and others (see AUTHORS.txt).
#
# The resources, libraries, and some source files under other terms (see NOTICE.txt).
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
autogator
=======
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
__license__ = "MIT"
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
SITE_DATA_DIR = pathlib.Path(_dirs.site_data_dir)
SITE_DATA_DIR.mkdir(parents=True, exist_ok=True)
# SITE_CONFIG_DIR = SITE_DATA_DIR / "config"

print("Welcome to AutoGator!")
print("© 2019-{}, CamachoLab".format(date.today().year))

import logging
logging.basicConfig(
    level=logging.INFO,
)
