# -*- coding: utf-8 -*-
#
# Copyright © Autogator Project Contributors
# Licensed under the terms of the GNU GPLv3+ License
# (see autogator/__init__.py for details)

import autogator.dataCache as glob


def startup():
    data_cache = glob.DataCache.get_instance()
    response = input("Would you like to Calibrate your Configuration? (y/n)")
    if response.lower().count("y") > 0:
        print("Calibrating...")
        data_cache.calibrate()
        data_cache.set_configuration()
        print("Calibrated")
    data_cache.get_configuration()
    print("Starting Up")
