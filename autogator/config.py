# -*- coding: utf-8 -*-
#
# Copyright © Autogator Project Contributors
# Licensed under the terms of the GNU GPLv3+ License
# (see autogator/__init__.py for details)

"""
Configuration Class
-------------------------------------

Stores configuration information for setup.
"""

from typing import Optional, Tuple, List
from pathlib import Path
import numpy as np
import os
from yaml import dump, safe_load


class Configuration:
    """
    Reads and writes key word argument configuration information with a yaml file.
    ...

    Attributes
    ----------
    file_path : str
        Direct file path to configuration yaml file.
    """

    def __init__(self, file_path) -> None:
        self.file_path = file_path
        if not file_path.exists():
            with file_path.open("w") as fout:
                fout.write("")
        with self.file_path.open("r") as fin:
            self.attrs = safe_load(fin)
        if self.attrs is None:
            self.attrs = {}

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

    def add_attr(self, key, value):
        if value.__class__ == np.ndarray:
            self.attrs[key] = value.tolist()
        elif value.__class__ == tuple:
            self.attrs[key] = list(value)
        else:
            self.attrs[key] = value

    def save(self):
        """
        Saves key words arguments in Configuration to yaml file.
        """
        with self.file_path.open("w") as fout:
            fout.write(dump(self.attrs))
