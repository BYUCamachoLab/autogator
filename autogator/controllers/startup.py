# -*- coding: utf-8 -*-
#
# Copyright © Autogator Project Contributors
# Licensed under the terms of the MIT License
# (see autogator/__init__.py for details)

import configparser

import autogator.config as cfg


def read_config():
    config = configparser.ConfigParser()
    config.read('config.ini')

    cfg.KINESIS_DLL_PATH = config['DEFAULT'].get('KINESIS_DLL_PATH')
    cfg.STAGE_X_SERIAL = config['DEFAULT'].getint('STAGE_X_SERIAL')
    cfg.STAGE_Y_SERIAL = config['DEFAULT'].getint('STAGE_Y_SERIAL')
    cfg.STAGE_ROT_SERIAL = config['DEFAULT'].getint('STAGE_ROT_SERIAL')


def startup():
    read_config()
