"""
This file acts as an object that holds objects that need to have persistance from the beginning to the end of the program
"""

from typing import Any
import autogator.expirement.platformcalibrator as cal
import autogator.config as cfg
import autogator.motion.state_machine.keyboardTesting as control
from pyrolab.api import locate_ns
from pyrolab.drivers.scopes.rohdeschwarz import RTO
from autogator.motion import motion

"""
Various Parameters to setup the nameserver object and Oscilliscope
"""
NAMESERVER_HOST = "camacholab.ee.byu.edu"
OSCILLISCOPE_IP_ADDRESS = "10.32.112.162"
OSCILLISCOPE_PROTOCOL = "INSTR"
PLATFORM_CALIBRATION_TEXT_FILE = "examples/circuits.txt"

class DataCache:
    __instance = None
    def __init__(self):
        if self.__instance != None:
            raise Exception("This Class is a Singleton")
        else:
            self.configuration = cfg.coord_config
            cfg.load_config()
            self.state_machine = control
            self.nameserver = locate_ns(host=NAMESERVER_HOST)
            self.oscilliscope = RTO(OSCILLISCOPE_IP_ADDRESS, protocol=OSCILLISCOPE_PROTOCOL)
            self.calibration = cal.PlatformCalibrator(text_file_name=PLATFORM_CALIBRATION_TEXT_FILE, oscilliscope=self.oscilliscope)
            self.motion = motion.Motion.get_instance()
            DataCache.__instance = self
    
    @staticmethod
    def get_instance():
        if DataCache.__instance == None:
            DataCache()
        return DataCache.__instance

    def load_configuration(self) -> None:
        cfg.load_config()
        
    def set_configuration(self) -> None:
        self.configuration = cfg.CoordinateConfiguration(self.calibration.get_config_parameters())
        self.configuration.save()

    def run_sm(self) -> None:
        self.state_machine.run()
    
    def calibrate(self) -> None:
        self.calibration.calibrate()
    
    def get_configuration(self) -> cfg.CoordinateConfiguration:
        return self.configuration
    
    def get_sm(self) -> control:
        return self.state_machine
    
    def get_nameserver(self) -> Any:
        return self.nameserver
    
    def get_oscilliscope(self) -> RTO:
        return self.oscilliscope
    
    def get_calibration(self) -> cal.PlatformCalibrator:
        return self.calibration
    
    def get_motion(self) -> motion.Motion:
        return self.motion