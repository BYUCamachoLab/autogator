# -*- coding: utf-8 -*-
#
# Copyright © Autogator Project Contributors
# Licensed under the terms of the GNU GPLv3+ License
# (see autogator/__init__.py for details)

"""
Platform Calibrator
-------------------

Contains logic for calculating the affine transformation between GDS and 
hardware stage coordinates.
"""

import numpy as np
import time
from typing import List


class PlatformCalibrator:
    def __init__(
        self, circuitMap=None, oscilliscope=None, dataScanner=None, motion=None
    ) -> None:
        self.oscope = oscilliscope
        self.circuitMap = circuitMap
        self.motion = motion
        self.dataScanner = dataScanner
        test_circuits = self.circuitMap.get_test_circuits()
        self.circuit1 = test_circuits[0]
        self.circuit2 = test_circuits[1]
        self.circuit3 = test_circuits[2]
        self.point1 = None
        self.point2 = None
        self.point3 = None
        self.origin = None
        self.conversion_matrix = None
        self.do_scan = "n"

    def calibrate(self) -> None:
        """
        Accepts the coordinates

        .. note:: Will ask to use dataScanner to optimize alignment, defaults to no if dataScanner not initialized.

        Returns
        -------
        conversion_matrix : np.array
            Affine tranformation to convert between GDS and Stage coordinates.
        """
        if self.dataScanner != None:
            self.do_scan = input("Do you want to do use autoscan? (y/n) Press Enter\n")
        else:
            self.do_scan = "n"
            print("Data Scanner is not Initialized, unable to perform Auto Scan")

        do_home = input("Do you want tohome the motors? (y/n) Press Enter\n")
        if do_home.lower() == "y":
            self.motion.home_motors()

        print("Starting calibration process...")

        self.point1 = self.keyloop_for_calibration(self.circuit1.ID)
        time.sleep(1)
        self.point2 = self.keyloop_for_calibration(self.circuit2.ID)
        time.sleep(1)
        self.point3 = self.keyloop_for_calibration(self.circuit3.ID)

        loc_1 = self.circuit1.location
        loc_2 = self.circuit2.location
        loc_3 = self.circuit3.location

        gds = np.array(
            [
                [float(loc_1[0]), float(loc_1[1]), 1, 0, 0, 0],
                [0, 0, 0, float(loc_1[0]), float(loc_1[1]), 1],
                [float(loc_2[0]), float(loc_2[1]), 1, 0, 0, 0],
                [0, 0, 0, float(loc_2[0]), float(loc_2[1]), 1],
                [float(loc_3[0]), float(loc_3[1]), 1, 0, 0, 0],
                [0, 0, 0, float(loc_3[0]), float(loc_3[1]), 1],
            ]
        )

        stage = np.array(
            [
                [self.point1[0]],
                [self.point1[1]],
                [self.point2[0]],
                [self.point2[1]],
                [self.point3[0]],
                [self.point3[1]],
            ]
        )

        a = np.linalg.inv(gds) @ stage

        self.conversion_matrix = np.array(
            [[a[0][0], a[1][0], a[2][0]], [a[3][0], a[4][0], a[5][0]], [0, 0, 1]]
        )
        return self.conversion_matrix

    # Don't know if works
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
        self.motion.origin = self.origin

        return self.origin

    def keyloop_for_calibration(self, circuit_id) -> List[float]:
        """
        Logic for moving to a specified circuit, optimizing alignment, and returning location.

        .. note:: Will not perform auto_scan if specified by do_scan or dataScanner is not intialized.

        Parameters
        ----------
        circuit_id : str
            The ID of the circuit to be moved to.

        Returns
        -------
        motor_coordinates : List[float]
            x and y coordinates of stage location after moving and optimizing.
        """
        print("Move " + circuit_id + " into Crosshairs, then press q")
        self.motion.keyloop()
        if self.do_scan == "y" and self.dataScanner != None:
            print("Optimizing alignment...")
            self.dataScanner.auto_scan()
            scan_again = input("Scan again? (y/n) Press Enter\n")
            while scan_again == "y":
                self.dataScanner.auto_scan()
                scan_again = input("Scan again? (y/n) Press Enter\n")
            print("Done.")
        else:
            print("No DataScanner initialized, cannot optimize alignment.")
        return [
            self.motion.get_motor_position(self.motion.x_mot),
            self.motion.get_motor_position(self.motion.y_mot),
        ]
