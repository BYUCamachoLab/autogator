# -*- coding: utf-8 -*-
#
# Copyright © Autogator Project Contributors
# Licensed under the terms of the MIT License
# (see autogator/__init__.py for details)

"""
autogator.config
----------------

All configuration settings that may be specific to a user or installation
can be loaded here. Defaults are provided, but the specifics are found
in 'config.ini'. Each time the program GUI is loaded, these parameters are
read and set. Each time the program is closed, these parameters are persisted
in 'config.ini'.

No functions or objects besides plain variables should appear in this file.
"""

KINESIS_DLL_PATH = "/"
STAGE_X_SERIAL = None
STAGE_Y_SERIAL = None
STAGE_ROT_SERIAL = None
