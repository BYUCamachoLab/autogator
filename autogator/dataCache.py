"""
This file acts as an object that holds objects that need to have persistance from call to call
This file will also perform simple actions such as:
 - Motion Control / Run State Machine
 - Calibrate
 - Setting the Configuration
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

from autogator import SITE_CONFIG_DIR
COORDINATE_DIR = SITE_CONFIG_DIR / "configuration"
COORDINATE_DIR.mkdir(parents=True, exist_ok=True)
COORD_FILE = "config.yaml"
CONFIG_FILE_PATH = COORDINATE_DIR / COORD_FILE

# A Singleton Class that holds persistent data
class DataCache:
    __instance = None

    def __init__(self):
        # Singleton Style
        if self.__instance != None:
            raise Exception("This Class is a Singleton")
        else:
            # # Sets base values
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
            self.motion = Motion(x_mot=Proxy(ns.lookup(self.x_mot_name)), y_mot=Proxy(ns.lookup(self.y_mot_name)), 
                r_mot=Proxy(ns.lookup(self.r_mot_name)), conversion_matrix=self.conversion_matrix)
            self.dataScanner = DataScanner(self.scope, self.motion)
            self.platformCalibrator = PlatformCalibrator(self.circuitMap, self.scope, self.dataScanner, self.motion)
            DataCache.__instance = self

    # Retrieves a singleton instance of the class
    @staticmethod
    def get_instance():
        # if there is no instance, this will instantiate the class
        if DataCache.__instance == None:
            DataCache()
        return DataCache.__instance

    def get_motion(self):
        return self.motion

    def get_laser(self):
        return self.laser

    def get_scope(self):
        return self.scope

    def get_circuitMap(self):
        return self.circuitMap

    def get_dataScanner(self):
        return self.dataScanner

    def get_platformCalibrator(self):
        return self.platformCalibrator

    def calibrate(self):
        self.configuration.attrs["conversion_matrix"] = self.platformCalibrator.calibrate().tolist()
        self.motion.set_conversion_matrix(self.configuration.attrs["conversion_matrix"])
        self.configuration.save()

    def set_circuitMap_path(self, new_path):
        self.configuration.attrs["circuitMap_file_path"] = new_path
        self.circuitMap_file_path = new_path
        self.circuitMap = CircuitMap(new_path)
        self.configuration.save()