from packages.motion import *
from packages.map import Map
from packages.dataScanner import DataScanner
import numpy as np
import os
os.add_dll_directory("C:\\Program Files\\Thorlabs\\Kinesis")
import keyboard

### Add lasor controls later, assume on for now

conversion_matrix = np.array([[1]])

point1 = [0,0]
point2 = [0,0]
point3 = [0,0]

class PlatformCalibrator:
    def __init__(self, text_file_name, oscilliscope):
        self.oscope = oscilliscope
        self.map = Map(text_file_name)
        self.dataScanner = DataScanner(self.oscope)

    def calibrate(self):
        circuits = self.map.return_circuits()
        global point1, point2, point3, conversion_matrix
        home_motors()
        print("Starting calibration process...")
        print("Move " + circuits[0].name + " into Crosshairs, then press q")
        self.keyloop_for_calibration_point1()
        print("Then Move " + circuits[1].name + " into Crosshairs, then press q")
        self.keyloop_for_calibration_point2()
        print("Then Move " + circuits[2].name + " into Crosshairs, then press q")
        self.keyloop_for_calibration_point3()
        location1 = circuits[0].location
        location2 = circuits[1].location
        location3 = circuits[2].location
        print("GDS locations:")
        print(location1)
        print(location2)
        print(location3)
        print("Chip locations:")
        print(point1)
        print(point2)
        print(point3)

        GDS = np.array([[float(location1[0]), float(location1[1]), 1, 0, 0, 0], [0, 0, 0, float(location1[0]), float(location1[1]), 1], [float(location2[0]), float(location2[1]), 1, 0, 0, 0], [0, 0, 0, float(location2[0]), float(location2[1]), 1], [float(location3[0]), float(location3[1]), 1, 0, 0, 0], [0, 0, 0, float(location3[0]), float(location3[1]), 1]])

        CHIP = np.array([[point1[0]],[point1[1]],[point2[0]],[point2[1]],[point3[0]],[point3[1]]])

        a = np.linalg.inv(GDS) @ CHIP

        conversion_matrix = np.array([[a[0][0], a[1][0], a[2][0]], [a[3][0], a[4][0], a[5][0]], [0, 0, 1]])


    def keyloop_for_calibration_point1(self):
        keyloop()
        global point1
        print("Optimizing data...")
        self.dataScanner.auto_scan()
        print("Done.")
        point1 = [get_x_position(), get_y_position()]
        print("Point 1 set to (" + str(point1[0]) + "," + str(point1[1]) + ")")

    def keyloop_for_calibration_point2(self):
        keyloop()
        global point2
        print("Optimizing data...")
        self.dataScanner.auto_scan()
        print("Done.")
        point2 = [get_x_position(), get_y_position()]
        print("Point 2 set to (" + str(point2[0]) + "," + str(point2[1]) + ")")

    def keyloop_for_calibration_point3(self):
        keyloop()
        global point3
        print("Optimizing data...")
        self.dataScanner.auto_scan()
        print("Done.")
        point3 = [get_x_position(), get_y_position()]
        print("Point 3 set to (" + str(point3[0]) + "," + str(point3[1]) + ")")

    def get_conversions_matrix():
        return conversion_matrix