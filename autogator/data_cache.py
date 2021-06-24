"""
This file acts as an object that holds objects that need to have persistance from call to call
This file will also perform simple actions such as:
 - Motion Control / Run State Machine
 - Calibrate
 - Setting the Configuration
"""

from typing import Any
import autogator.expirement.platform_calibrator as cal
import autogator.config as cfg
import autogator.motion.state_machine.sync_sm as control
from pyrolab.api import locate_ns
from pyrolab.drivers.scopes.rohdeschwarz import RTO
from autogator.motion import motion

"""
Various Parameters to setup the nameserver object and Oscilliscope
"""
NAMESERVER_HOST = "camacholab.ee.byu.edu"
OSCILLISCOPE_IP_ADDRESS = "10.32.112.162"
OSCILLISCOPE_PROTOCOL = "INSTR"
PLATFORM_CALIBRATION_TEXT_FILE = "circuits_test.txt"

# A Singleton Class that holds persistent data
class DataCache:
    __instance = None

    def __init__(self):
        # Singleton Style
        if self.__instance != None:
            raise Exception("This Class is a Singleton")
        else:
            # Sets base values
            self.configuration = cfg.coord_config
            cfg.load_config()
            self.state_machine = control
            self.nameserver = locate_ns(host=NAMESERVER_HOST)
            laser_available = (
                True
                if input("Is The Laser Available for use? (y/n) \n") == "y"
                else False
            )
            if laser_available:
                self.oscilliscope = RTO(
                    OSCILLISCOPE_IP_ADDRESS, protocol=OSCILLISCOPE_PROTOCOL
                )
            else:
                self.oscilliscope = None
            self.calibration = cal.PlatformCalibrator(
                text_file_name=PLATFORM_CALIBRATION_TEXT_FILE,
                oscilliscope=self.oscilliscope,
            )
            self.motion = motion.Motion.get_instance()
            DataCache.__instance = self

    # Retrieves a singleton instance of the class
    @staticmethod
    def get_instance():
        # if there is no instance, this will instantiate the class
        if DataCache.__instance == None:
            DataCache()
        return DataCache.__instance

    # This will load the configuration
    def load_configuration(self) -> None:
        cfg.load_config()
        print(cfg.coord_config.to_dict())
        self.calibration.set_config_parameters(
            cfg.coord_config.coordinate_1,
            cfg.coord_config.coordinate_2,
            cfg.coord_config.coordinate_3,
            cfg.coord_config.origin,
            cfg.coord_config.affine,
        )
        self.motion.set_conversion_matrix(cfg.coord_config.affine)
        self.motion.set_origin(cfg.coord_config.origin)

    # This will set the configuration
    def set_configuration(self) -> None:
        (
            rotation,
            point1,
            point2,
            point3,
            origin,
            affine,
        ) = self.calibration.get_config_parameters()
        cfg.save_config(rotation, point1, point2, point3, origin, affine)

    # This will run the motion control state machine
    def run_sm(self) -> None:
        self.state_machine.run()

    # This will perform the calibration
    def calibrate(self) -> None:
        self.calibration.calibrate()

    # Origin calibration
    def concentric_calibration(self) -> None:
        self.calibration.rotational_calibration()

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
