
# -*- coding: utf-8 -*-
#
# Copyright © Simphony Project Contributors
# Licensed under the terms of the MIT License
# (see simphony/__init__.py for details)

import configparser

def write_config():
    config = configparser.ConfigParser()

    config['DEFAULT'] = {
        'stage_x': '27003497',
        'stage_y': '27504851',
        'stage_rot': '27003323',
    }

    with open('config.ini', 'w') as configfile:
        config.write(configfile)

def read_config():
    config = configparser.ConfigParser()

    config.read('config.ini')

    return config
