# -*- coding: utf-8 -*-
#
# Copyright © Autogator Project Contributors
# Licensed under the terms of the MIT License
# (see autogator/__init__.py for details)

import autogator.global_objects as glob

def startup():
    globals_obj = glob.globals_obj
    response = input("Would you like to Calibrate your Configuration? (y/n)")
    if response.lower().count("y") > 0:
        print("Calibrating...")
        globals_obj.calibrate()
        globals_obj.set_configuration()
        print("Calibrated")
    globals_obj.get_configuration()
    print("Starting Up")
