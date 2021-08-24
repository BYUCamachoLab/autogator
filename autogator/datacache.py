# -*- coding: utf-8 -*-
#
# Copyright © Autogator Project Contributors
# Licensed under the terms of the MIT License
# (see autogator/__init__.py for details)

"""
Data Cache
----------

Instantiates and holds objects of remote instruments to be used by files that import it.
"""

import sys
from typing import Any
from pathlib import Path

import numpy as np
from pyrolab.api import locate_ns, Proxy
from pyrolab.drivers.scopes.rohdeschwarz import RTO
from Pyro5.api import locate_ns, Proxy

from autogator.platformcalibrator import PlatformCalibrator
from autogator.config import Configuration
from autogator.motion import Motion
from autogator.datascanner import DataScanner
from autogator.circuitmap import CircuitMap
from autogator import SITE_CONFIG_DIR
import autogator.interfaces as interfaces

COORDINATE_DIR = SITE_CONFIG_DIR / "configuration"
COORDINATE_DIR.mkdir(parents=True, exist_ok=True)
COORD_FILE = "config.yaml"
CONFIG_FILE_PATH = COORDINATE_DIR / COORD_FILE


def do_nothing(*args, **kwargs):
    return None


class Void:
    def __getattr__(self, key):
        return do_nothing


class DataCache:
    """
    Reads and writes key word argument configuration information with a yaml file.

    .. note:: Singleton Class
    ...

    Attributes
    ----------
    file_path : str
        Direct file path to configuration yaml file.
    """

    __instance = None

    def __init__(self, omits=[]):
        if self.__instance != None:
            raise Exception("This Class is a Singleton")
        else:
            self.configuration = Configuration(CONFIG_FILE_PATH)

            if "scope" not in omits and "s" not in omits:
                self.scope_info = self.configuration.attrs["scope_info"]
                self.scope = getattr(interfaces, self.scope_info["classname"])(
                    self.scope_info
                )
            else:
                self.scope = Void()

            if "laser" not in omits and "l" not in omits:
                self.laser_info = self.configuration.attrs["laser_info"]
                self.laser = getattr(interfaces, self.laser_info["classname"])(
                    self.laser_info
                )
            else:
                self.laser = Void()

            if "conversion_matrix" in self.configuration.attrs.keys():
                self.conversion_matrix = self.configuration.attrs["conversion_matrix"]
            else:
                self.conversion_matrix = None

            if "motors" not in omits and "m" not in omits:
                if "x_mot" not in omits and "x" not in omits:
                    self.x_mot_info = self.configuration.attrs["x_mot_info"]
                    x_mot = getattr(interfaces, self.x_mot_info["classname"])(
                        self.x_mot_info
                    )
                else:
                    x_mot = Void()

                if "y_mot" not in omits and "y" not in omits:
                    self.y_mot_info = self.configuration.attrs["y_mot_info"]
                    y_mot = getattr(interfaces, self.y_mot_info["classname"])(
                        self.y_mot_info
                    )
                else:
                    y_mot = Void()

                if "r_mot" not in omits and "r" not in omits:
                    self.r_mot_info = self.configuration.attrs["r_mot_info"]
                    r_mot = getattr(interfaces, self.r_mot_info["classname"])(
                        self.r_mot_info
                    )
                else:
                    r_mot = Void()

                self.motion = Motion(
                    x_mot=x_mot,
                    y_mot=y_mot,
                    r_mot=r_mot,
                    conversion_matrix=self.conversion_matrix,
                )
            else:
                self.motion = Void()

            if "circuitMap_file_path" in self.configuration.attrs.keys():
                self.circuitMap_file_path = self.configuration.attrs[
                    "circuitMap_file_path"
                ]
            else:
                self.circuitMap_file_path = None
            self.circuitMap = CircuitMap.loadtxt(self.circuitMap_file_path)

            if "load_position" in self.configuration.attrs.keys():
                self.load_position = self.configuration.attrs["load_position"]
            else:
                self.load_position = None

            if "unload_position" in self.configuration.attrs.keys():
                self.unload_position = self.configuration.attrs["unload_position"]
            else:
                self.unload_position = None

            if not isinstance(self.motion, Void) and not isinstance(self.scope, Void):
                self.dataScanner = DataScanner(self.scope, self.motion)
                self.platformCalibrator = PlatformCalibrator(
                    self.circuitMap, self.scope, self.dataScanner, self.motion
                )
            else:
                self.dataScanner = Void()
                self.platformCalibrator = Void()

            self.configuration.save()

            DataCache.__instance = self

    @staticmethod
    def get_instance():
        """
        Retrieves singleton instance of DataCache or creates an instance if none exist.

        Returns
        -------
        instance : DataCache
            Singleton instance of dataCache.
        """
        if DataCache.__instance == None:
            DataCache(omits=sys.argv)
        return DataCache.__instance

    def get_motion(self):
        """
        Retrieves motion object of dataCache.

        Returns
        -------
        motion : Motion
            Motion object of dataCache.
        """
        return self.motion

    def get_laser(self):
        """
        Retrieves laser object of dataCache.

        Returns
        -------
        laser : TSL550
            Laser object of dataCache.
        """
        return self.laser

    def get_scope(self):
        """
        Retrieves oscilliscope object of dataCache.

        Returns
        -------
        scope : RTO
            Oscilliscope object of dataCache.
        """
        return self.scope

    def get_circuitMap(self):
        """
        Retrieves circuitMap object of dataCache.

        Returns
        -------
        circuitMap : CircuitMap
            CircuitMap object of dataCache.
        """
        return self.circuitMap

    def get_dataScanner(self):
        """
        Retrieves dataScanner object of dataCache.

        Returns
        -------
        dataScanner : DataScanner
            DataScanner object of dataCache.
        """
        return self.dataScanner

    def get_platformCalibrator(self):
        """
        Retrieves platformCalibrator object of dataCache.

        Returns
        -------
        platformCalibrator : PlatformCalibrator
            PlatformCalibrator object of dataCache.
        """
        return self.platformCalibrator

    def calibrate(self):
        """
        Calls calibrate function of platformCalibrator and sets new conversion matrix to motion and configuration
        """
        self.configuration.attrs[
            "conversion_matrix"
        ] = self.platformCalibrator.calibrate().tolist()
        self.motion.conversion_matrix = self.configuration.attrs["conversion_matrix"]
        self.configuration.save()

    def set_circuitMap_path(self, new_path):
        """
        Sets a new circuitMap file in dataCache and saves it to configuration.

        Parameters
        ----------
        new_path : str
            Direct path to text file for new circuitMap.
        """
        self.configuration.attrs["circuitMap_file_path"] = new_path
        self.circuitMap_file_path = new_path
        self.circuitMap = CircuitMap(new_path)
        self.configuration.save()
