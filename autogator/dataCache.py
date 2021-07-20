# -*- coding: utf-8 -*-
#
# Copyright © Autogator Project Contributors
# Licensed under the terms of the GNU GPLv3+ License
# (see autogator/__init__.py for details)

"""
DataCache Class
-------------------------------------

Instantiates and holds objects of remote instruments to be used by files that import it.
"""

import numpy as np
from typing import Any
from pathlib import Path
from autogator.platformCalibrator import PlatformCalibrator
from autogator.config import Configuration
from autogator.motion import Motion
from autogator.dataScanner import DataScanner
from autogator.circuitMap import CircuitMap
from pyrolab.api import locate_ns, Proxy
from pyrolab.drivers.scopes.rohdeschwarz import RTO
from pyrolab.drivers.lasers.tsl550 import TSL550
from pyrolab.drivers.motion.z825b import Z825B
from pyrolab.drivers.motion.prm1z8 import PRM1Z8

from autogator import SITE_CONFIG_DIR
COORDINATE_DIR = SITE_CONFIG_DIR / "configuration"
COORDINATE_DIR.mkdir(parents=True, exist_ok=True)
COORD_FILE = "config.yaml"
CONFIG_FILE_PATH = COORDINATE_DIR / COORD_FILE

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

    def __init__(self):
        if self.__instance != None:
            raise Exception("This Class is a Singleton")
        else:
            self.configuration = Configuration(CONFIG_FILE_PATH)

            # self.configuration.add_attr("name_server", "camacholab.ee.byu.edu")
            # self.configuration.add_attr("scope_IP", "10.32.112.162")
            # self.configuration.add_attr("scope_protocol", "INSTR")
            # self.configuration.add_attr("scope_timeout", 10000)
            # self.configuration.add_attr("laser_name", "TSL550")
            # self.configuration.add_attr("circuitMap_file_path", "C:\\Users\\mcgeo\\source\\repos\\autogator\\examples\\circuits.txt")
            # self.configuration.add_attr("x_mot_name", "asgard.captainamerica")
            # self.configuration.add_attr("y_mot_name", "asgard.hulk")
            # self.configuration.add_attr("r_mot_name","asgard.wolverine" )
            # self.configuration.add_attr("conversion_matrix", np.array([[-20.0010097705223880598, 1.3603921568627669e-05, 7.52609524692713], 
            #     [-1.3085820895522213e-05, -0.0010064993464052288, 6.455855622622184], [0.0, 0.0, 1.0]]))

            # self.configuration.save()

            ns = locate_ns(self.configuration.attrs["name_server"])
            self.scope_IP = self.configuration.attrs["scope_IP"]
            self.scope_protocol = self.configuration.attrs["scope_protocol"]
            self.scope_timeout = self.configuration.attrs["scope_timeout"]
            self.laser_name = self.configuration.attrs["laser_name"]
            self.circuitMap_file_path = self.configuration.attrs["circuitMap_file_path"]
            self.x_mot_name = self.configuration.attrs["x_mot_name"]
            self.y_mot_name = self.configuration.attrs["y_mot_name"]
            self.r_mot_name = self.configuration.attrs["r_mot_name"]
            self.conversion_matrix = self.configuration.attrs["conversion_matrix"]

            self.scope = RTO(self.scope_IP, protocol=self.scope_protocol, timeout=self.scope_timeout)
            self.laser = Proxy(ns.lookup(self.laser_name))
            self.circuitMap = CircuitMap(text_file_path=self.circuitMap_file_path)
            self.motion = Motion(x_mot=Z825B(), y_mot=Z825B(), r_mot=PRM1Z8(), conversion_matrix=self.conversion_matrix)
                # x_mot=Proxy(ns.lookup(self.x_mot_name)), y_mot=Proxy(ns.lookup(self.y_mot_name)), 
                # r_mot=Proxy(ns.lookup(self.r_mot_name)), conversion_matrix=self.conversion_matrix)
            self.dataScanner = DataScanner(self.scope, self.motion)
            self.platformCalibrator = PlatformCalibrator(self.circuitMap, self.scope, self.dataScanner, self.motion)
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
            DataCache()
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
        self.configuration.attrs["conversion_matrix"] = self.platformCalibrator.calibrate().tolist()
        self.motion.set_conversion_matrix(self.configuration.attrs["conversion_matrix"])
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