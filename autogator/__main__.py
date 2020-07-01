# -*- coding: utf-8 -*-
#
# Copyright © Autogator Project Contributors
# Licensed under the terms of the MIT License
# (see autogator/__init__.py for details)

from datetime import date
import configparser
import atexit

import autogator.config as cfg
from autogator.mainwindow import start_gui


def write_config():
    module = globals().get('cfg', None)
    if module:
        settings = {key: value for key, value in module.__dict__.items() if not (key.startswith('__') or key.startswith('_'))}
    else:
        return

    config = configparser.ConfigParser()
    config['DEFAULT'] = settings

    with open('config.ini', 'w') as configfile:
        config.write(configfile)

def read_config():
    config = configparser.ConfigParser()
    config.read('config.ini')

    cfg.KINESIS_DLL_PATH = config['DEFAULT'].get('KINESIS_DLL_PATH')
    cfg.STAGE_X_SERIAL = config['DEFAULT'].getint('STAGE_X_SERIAL')
    cfg.STAGE_Y_SERIAL = config['DEFAULT'].getint('STAGE_Y_SERIAL')
    cfg.STAGE_ROT_SERIAL = config['DEFAULT'].getint('STAGE_ROT_SERIAL')

@atexit.register
def onclose():
    print("Saving configurations and closing...", end='')
    write_config()
    print("DONE")

if __name__ == "__main__":
    print("Welcome to Autogator!")
    print("© 2019-{}, CamachoLab".format(date.today().year))
    read_config()

    start_gui()
