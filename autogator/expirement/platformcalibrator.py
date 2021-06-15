from autogator.motion import motion
from autogator.map.map import Map
from autogator.expirement.datascanner import DataScanner
import numpy as np
import autogator.motion.state_machine.keyboardTesting as key_test



### Add lasor controls later, assume on for now

class PlatformCalibrator:
    def __init__(self, text_file_name, oscilliscope):
        self.oscope = oscilliscope
        self.map = Map(text_file_name)
        self.motion = motion.Motion()
        self.dataScanner = DataScanner(self.oscope, self.motion)
        self.point1=[0,0]
        self.point2=[0,0]
        self.point3=[0,0]
        self.conversion_matrix= np.array([[1]])

    def calibrate(self):
        circuits = self.map.return_circuits()
        self.motion.home_motors()
        print("Starting calibration process...")
        print("Move " + circuits[0].id + "\n" + circuits[0].name + " into Crosshairs, then press q")
        self.point1=self.keyloop_for_calibration()
        print("Point 1 set to (" + str(self.point1[0]) + "," + str(self.point1[1]) + ")")

        print("Then Move " + circuits[1].id + "\n" + circuits[1].name + " into Crosshairs, then press q")
        self.point2=self.keyloop_for_calibration()
        print("Point 2 set to (" + str(self.point2[0]) + "," + str(self.point2[1]) + ")")

        print("Then Move " + circuits[2].id + "\n" + circuits[2].name + " into Crosshairs, then press q")
        self.point3=self.keyloop_for_calibration()
        print("Point 3 set to (" + str(self.point3[0]) + "," + str(self.point3[1]) + ")")

        location1 = circuits[0].location
        location2 = circuits[1].location
        location3 = circuits[2].location
        print("GDS locations:")
        print(location1)
        print(location2)
        print(location3)
        print("Chip locations:")
        print(self.point1)
        print(self.point2)
        print(self.point3)

        GDS = np.array([[float(location1[0]), float(location1[1]), 1, 0, 0, 0], [0, 0, 0, float(location1[0]), float(location1[1]), 1], [float(location2[0]), float(location2[1]), 1, 0, 0, 0], [0, 0, 0, float(location2[0]), float(location2[1]), 1], [float(location3[0]), float(location3[1]), 1, 0, 0, 0], [0, 0, 0, float(location3[0]), float(location3[1]), 1]])

        CHIP = np.array([[self.point1[0]],[self.point1[1]],[self.point2[0]],[self.point2[1]],[self.point3[0]],[self.point3[1]]])

        a = np.linalg.inv(GDS) @ CHIP

        self.conversion_matrix = np.array([[a[0][0], a[1][0], a[2][0]], [a[3][0], a[4][0], a[5][0]], [0, 0, 1]])

    def keyloop_for_calibration(self):
        key_test.run(self.motion)
        #print("Optimizing data...")
        #self.dataScanner.auto_scan()
        print("Done.")
        return [self.motion.get_x_position(), self.motion.get_y_position()]

    def get_conversions_matrix(self):
        return self.conversion_matrix
    
    def get_config_parameters(self):
        return self.motion.get_r_position(), self.point1, self.point2, self.point3, self.conversion_matrix
    
