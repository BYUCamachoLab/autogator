# -*- coding: utf-8 -*-
#
# Copyright © PyroLab Project Contributors
# Licensed under the terms of the GNU GPLv3+ License
# (see pyrolab/__init__.py for details)

from typing import Optional, Tuple, List
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

    _valid_attributes = ["COORDINATE_X", "COORDINATE_Y"]

    def __init__(self, **kwargs) -> None:
        self.attrs = {}
        for key, value in kwargs.items():
            print(value.__class__)
            if value.__class__ == np.ndarray:
                self.attrs[key] = value.tolist()
            elif value.__class__ == tuple:
                self.attrs[key] = list(value)
            else:
                self.attrs[key] = value

    # Gets and attribute associated with the key
    def __getattr__(self, key):
        return self.attrs[key]

    def __str__(self):
        output = "\n"
        for key in self.attrs:
            output += key + ": " + str(self.attrs[key]) + "\n"
        return output

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
            fout.write(dump(self.attrs))

    def load(self):
        """
        Read the configuration from a file.
        """
        filename = COORDINATE_DIR / COORD_FILE

        if not os.path.exists(filename):
            self.save()

        with filename.open("r") as fin:
            d = safe_load(fin)

        return self.from_dict(d)


coord_config = CoordinateConfiguration()


def load_config():
    global coord_config
    coord_config = coord_config.load()
    print(coord_config)


def save_config(
    input_rotation: float = 0.0,
    input_coordinate_1: List[float] = [0.0, 0.0],
    input_coordinate_2: List[float] = [0.0, 0.0],
    input_coordinate_3: List[float] = [0.0, 0.0],
    input_origin: List[float] = [0.0, 0.0],
    input_affine: np.array = np.array(
        object=[[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]
    ),
) -> None:
    global coord_config
    coord_config = CoordinateConfiguration(
        rotation=input_rotation,
        coordinate_1=input_coordinate_1,
        coordinate_2=input_coordinate_2,
        coordinate_3=input_coordinate_3,
        origin=input_origin,
        affine=input_affine,
    )
    coord_config.save()
    print(coord_config)
