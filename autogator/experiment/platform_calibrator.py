from pyrolab.drivers.scopes.rohdeschwarz import RTO
from autogator.motion import motion
from autogator.map import Map
from autogator.experiment.data_scanner import DataScanner
import numpy as np
import autogator.motion.state_machine.sync_sm as key_test
import time

### Add lasor controls later, assume on for now
class PlatformCalibrator:
    def __init__(self, text_file_name: str, oscilliscope: RTO = None) -> None:
        # Resets Basic Values
        self.oscope = oscilliscope
        self.map = Map(text_file_name)
        self.motion = motion.Motion.get_instance()
        if self.oscope != None:
            self.dataScanner = DataScanner(self.oscope, self.motion)
        else:
            self.dataScanner = None
        test_circuits = self.map.get_test_circuits()
        self.circuit1 = test_circuits[0]
        self.circuit2 = test_circuits[1]
        self.circuit3 = test_circuits[2]
        self.point1 = None
        self.point2 = None
        self.point3 = None
        self.origin = None
        self.conversion_matrix = None
        self.do_scan = "n"

    # Runs the calibration
    def calibrate(self) -> None:
        if self.dataScanner != None:
            self.do_scan = input("Do you want to do use autoscan? (y/n) Press Enter\n")
        else:
            self.do_scan = "n"
            print("Data Scanner is not Initialized, unable to perform Auto Scan")

        do_home = input("Do you want to home the motors? (y/n) Press Enter\n")
        # Reset the Motors to base location
        if do_home.lower() == "y":
            self.motion.home_motors()

        print("Starting calibration process...")

        # Getting the First point of Calibration
        print(
            "Move "
            + self.circuit1.ID
            + "\n"
            + self.circuit1.name
            + " into Crosshairs, then press q"
        )
        self.point1 = self.keyloop_for_calibration()
        print(
            "Point 1 set to (" + str(self.point1[0]) + "," + str(self.point1[1]) + ")"
        )
        time.sleep(1)

        # Getting the Second point of Calibration
        print(
            "Then Move "
            + self.circuit2.ID
            + "\n"
            + self.circuit2.name
            + " into Crosshairs, then press q"
        )
        self.point2 = self.keyloop_for_calibration()
        print(
            "Point 2 set to (" + str(self.point2[0]) + "," + str(self.point2[1]) + ")"
        )
        time.sleep(1)  # Getting the Third point of Calibration
        print(
            "Then Move "
            + self.circuit3.ID
            + "\n"
            + self.circuit3.name
            + " into Crosshairs, then press q"
        )
        self.point3 = self.keyloop_for_calibration()
        print(
            "Point 3 set to (" + str(self.point3[0]) + "," + str(self.point3[1]) + ")"
        )

        # Getting Locations and Showing Results
        location1 = self.circuit1.location
        location2 = self.circuit2.location
        location3 = self.circuit3.location
        print("GDS locations:")
        print(location1)
        print(location2)
        print(location3)
        print("Chip locations:")
        print(self.point1)
        print(self.point2)
        print(self.point3)

        # Affine Matrix Transformation of two vector spaces with different origins
        GDS = np.array(
            [
                [float(location1[0]), float(location1[1]), 1, 0, 0, 0],
                [0, 0, 0, float(location1[0]), float(location1[1]), 1],
                [float(location2[0]), float(location2[1]), 1, 0, 0, 0],
                [0, 0, 0, float(location2[0]), float(location2[1]), 1],
                [float(location3[0]), float(location3[1]), 1, 0, 0, 0],
                [0, 0, 0, float(location3[0]), float(location3[1]), 1],
            ]
        )

        CHIP = np.array(
            [
                [self.point1[0]],
                [self.point1[1]],
                [self.point2[0]],
                [self.point2[1]],
                [self.point3[0]],
                [self.point3[1]],
            ]
        )

        a = np.linalg.inv(GDS) @ CHIP

        self.conversion_matrix = np.array(
            [[a[0][0], a[1][0], a[2][0]], [a[3][0], a[4][0], a[5][0]], [0, 0, 1]]
        )
        self.motion.set_conversion_matrix(self.conversion_matrix)

    def rotational_calibration(self) -> None:
        if self.dataScanner != None:
            self.do_scan = input("Do you want to do use autoscan? (y/n) Press Enter\n")
        else:
            self.do_scan = "n"
            print("Data Scanner is not Initialized, unable to perform Auto Scan")

        print("Starting Calibration Process...")

        # Getting the First point of Calibration
        print(
            "Move "
            + self.circuit1.ID
            + "\n"
            + self.circuit1.name
            + " into Crosshairs, then press q"
        )
        point11 = self.point1
        point21 = self.point2
        self.motion.move_step(self.motion.r_mot, "forward")

        # Getting the First point of Calibration
        print(
            "Move "
            + self.circuit1.ID
            + "\n"
            + self.circuit1.name
            + " into Crosshairs, then press q"
        )
        point12 = self.keyloop_for_calibration()
        print("Point 1 set to (" + str(point12[0]) + "," + str(point12[1]) + ")")
        time.sleep(1)

        # Getting the Second point of Calibration
        print(
            "Then Move "
            + self.circuit2.ID
            + "\n"
            + self.circuit2.name
            + " into Crosshairs, then press q"
        )
        point22 = self.keyloop_for_calibration()
        print("Point 2 set to (" + str(point22[0]) + "," + str(point22[1]) + ")")

        self.motion.move_step(self.motion.r_mot, "backward")

        # Affine Matrix Transformation of two vector spaces with different origins
        p1_x_bar = (point11[0] + point12[0]) / 2.0
        p1_y_bar = (point11[1] + point12[1]) / 2.0
        p1_slope = (point11[0] - point12[0]) / (point12[1] - point11[1])

        p2_x_bar = (point21[0] + point22[0]) / 2.0
        p2_y_bar = (point21[1] + point22[1]) / 2.0
        p2_slope = (point21[0] - point22[0]) / (point22[1] - point21[1])

        c1 = (p1_slope * (-p1_x_bar)) + p1_y_bar
        c2 = (p2_slope * (-p2_x_bar)) + p2_y_bar
        x = (c2 - c1) / (p1_slope - p2_slope)
        y = (p1_slope * x) + c1

        self.origin = [x, y]
        self.motion.set_origin(self.origin)

        return self.origin

    # Performs motor functions to calibrate
    def keyloop_for_calibration(self) -> list[float]:
        key_test.run(self.motion)
        if self.do_scan.lower == "y" and self.dataScanner != None:
            print("Optimizing data...")
            self.dataScanner.auto_scan()
        print("Done.")
        return [self.motion.get_x_position(), self.motion.get_y_position()]

    # Returns the conversion matrix
    def get_conversions_matrix(self) -> np.array:
        return self.conversion_matrix

    # Returns Parameters used in the configuration
    def get_config_parameters(self):
        return (
            self.motion.get_r_position(),
            self.point1,
            self.point2,
            self.point3,
            self.origin,
            self.conversion_matrix,
        )

    # Sets Parameters used in the configuration
    def set_config_parameters(self, point1, point2, point3, origin, conversion_matrix):
        self.point1 = point1
        self.point2 = point2
        self.point3 = point3
        self.origin = origin
        self.conversion_matrix = conversion_matrix

    # Sets Parameters needed from the Config
    def set_parameters(self, r_motor, affine: np.array) -> None:
        self.motion.set_rotation(r_motor)
        self.conversion_matrix = affine
        self.motion.set_conversion_matrix(affine)