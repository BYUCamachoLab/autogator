# -*- coding: utf-8 -*-
#
# Copyright © Autogator Project Contributors
# Licensed under the terms of the MIT License
# (see autogator/__init__.py for details)

import configparser

import autogator.config as cfg


def write_config():
    print("Saving configurations...", end='')
    module = globals().get('cfg', None)
    if module:
        settings = {key: value for key, value in module.__dict__.items() if not (key.startswith('__') or key.startswith('_'))}
    else:
        return

    config = configparser.ConfigParser()
    config['DEFAULT'] = settings

    with open('config.ini', 'w') as configfile:
        config.write(configfile)
    print("DONE")


def shutdown():
    write_config()
