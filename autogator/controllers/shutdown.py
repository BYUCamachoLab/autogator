# -*- coding: utf-8 -*-
#
# Copyright © Autogator Project Contributors
# Licensed under the terms of the MIT License
# (see autogator/__init__.py for details)

import configparser

import autogator.config as cfg
import autogator.expirement.platformcalibrator as cal

import autogator.dataCache as data


def shutdown():
    dataCache = data.DataCache.get_instance()
    response = input("Would you like to save your configurations? (y/n)")
    if response.lower().count("y") > 0:
        print("Saving...")
        dataCache.set_configuration()
        print("Saved")
    print("Shutting Down")
