# -*- coding: utf-8 -*-
#
# Copyright © PyroLab Project Contributors
# Licensed under the terms of the GNU GPLv3+ License
# (see pyrolab/__init__.py for details)

from typing import Optional, Tuple
from pathlib import Path
import numpy as np
import os

from yaml import dump, safe_load

from autogator import SITE_CONFIG_DIR


COORDINATE_DIR = SITE_CONFIG_DIR / "coordinate"
COORDINATE_DIR.mkdir(parents=True, exist_ok=True)


COORD_FILE = "coord_config.yaml"

class CoordinateConfiguration:
    """
    Coordinate configuration object.
    Parameters
    ----------
    X Coordinate : float
        The X coordinate being saved
    coordinate_x
    Y Coordinate : float
        The Y coordinate being saved
    coordinate_y
    """
    _valid_attributes = [
        'COORDINATE_X', 'COORDINATE_Y'
    ]
    def __init__(self,
                 rotation: float=0.0,
                 coordinate_1: Tuple[float,float]=(0.0,0.0),
                 coordinate_2: Tuple[float,float]=(0.0,0.0),
                 coordinate_3: Tuple[float,float]=(0.0,0.0),
                 affine: np.array=np.array(object=[])) -> None:
        self.rotation = rotation
        self.coordinate_1 = coordinate_1
        self.coordinate_2 = coordinate_2
        self.coordinate_3 = coordinate_3
        self.affine = affine

    @classmethod
    def from_dict(cls, d):
        return cls(**d)

    def to_dict(self):
        return self.__dict__

    def save(self):
        """
        Writes the configuration to a file.
        """
        filename = COORDINATE_DIR / COORD_FILE
        with filename.open("w") as fout:
            fout.write(dump(self.to_dict()))

    def load(self):
        """
        Read the configuration from a file.
        """
        filename = COORDINATE_DIR / COORD_FILE
        
        if not os.path.exists(filename):
            return

        with filename.open("r") as fin:
            d = safe_load(fin)
            
        return self.from_dict(d)

coord_config = CoordinateConfiguration()

def load_config():
    global coord_config
    coord_config = coord_config.load()
