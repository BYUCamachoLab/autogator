# -*- coding: utf-8 -*-
#
# Copyright © Autogator Project Contributors
# Licensed under the terms of the MIT License
# (see autogator/__init__.py for details)

import configparser

import autogator.config as cfg
import autogator.expirement.platformcalibrator as cal

from autogator import globals


def shutdown():
    global_obj = globals.globals()
    response = input("Would you like to save your configurations? (y/n)")
    if response.lower().count("y") > 0:
        print("Saving...")
        global_obj.set_configuration()
        print("Saved")
    print("Shutting Down")
