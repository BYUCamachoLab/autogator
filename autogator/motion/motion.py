from ctypes import c_int, c_double, byref, pointer
import numpy as np
import time
import keyboard
import os
import autogator.map as map
import math
from autogator.data_cache import DataCache

from pyrolab.api import locate_ns, Proxy

ns = locate_ns(host="camacholab.ee.byu.edu")

help_txt = """\nControls\n--------\n
    \tleft arrow - jog move left
    \tright arrow - jog move right
    \tdown arrow - jog move down
    \tup arrow - jog move up
    \tc - jog clockwise rotation
    \tx - jog counterclockwise rotation
    \ta - continuous move left
    \td - continuous move right
    \ts - continuous move down
    \tw - continuous move up
    \tshift + j - jog step size (linear motors)
    \tshift + g - jog step size (rotational motor)
    \tshift + k - set velocity (mm/s)
    \tshift + r - recalibrate the conversion matrix
    \tshift + t - recalibrate origin for concentric rotation
    \tshift + f - Go To GDS Coordinate
    \tspacebar - emergency stop all
    \to - home linear motors
    \th - help
    \tq - quit
    """
NO_CHARACTER_KEYS = [
    "left arrow",
    "right arrow",
    "down arrow",
    "up arrow",
    "shift",
    "ctrl",
    "alt",
    "caps lock",
]


def is_no_char_key(input) -> bool:
    str_input = str(input).replace("KeyboardEvent(", "").replace(" down)", "")
    if str_input.count("up") != 0:
        return True
    output = False
    for key in NO_CHARACTER_KEYS:
        output |= str_input == key
    return output


def clear():
    keystrokes = keyboard.stop_recording()
    count = 0
    for stroke in keystrokes:
        if not is_no_char_key(stroke):
            keyboard.write("\b")
            count += 1
    print(
        "There were a total of "
        + str(len(keystrokes))
        + " keys recorded and "
        + str(count)
        + " deleted"
    )


class Motion:
    __instance = None

    def __init__(self):
        # Singleton Method
        if Motion.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            # Gets the motors
            self.x_mot = Proxy(ns.lookup("KCUBE_LAT"))
            self.y_mot = Proxy(ns.lookup("KCUBE_LON"))
            self.r_mot = Proxy(ns.lookup("KCUBE_ROT"))
            self.motors = [self.x_mot, self.y_mot, self.r_mot]

            for motor in self.motors:
                motor.autoconnect()
                motor.lock()

            self.conversion_matrix = None
            self.origin = None

            # Sets these to false so that motors can move without intereference
            self.x_mot_moving = False
            self.y_mot_moving = False
            self.r_mot_moving = False

            # Used for rotating the conversion Matrix
            self.gds_matrix = None
            self.point1 = None
            self.point2 = None
            self.point3 = None

            # key flags, boolean of whether they are pressed
            self.flags = {
                "left_arrow_pressed": False,
                "left_arrow_released": False,
                "right_arrow_pressed": False,
                "right_arrow_released": False,
                "up_arrow_pressed": False,
                "up_arrow_released": False,
                "down_arrow_pressed": False,
                "down_arrow_released": False,
                "c_pressed": False,
                "c_released": False,
                "x_pressed": False,
                "x_released": False,
                "a_pressed": False,
                "a_released": False,
                "d_pressed": False,
                "d_released": False,
                "w_pressed": False,
                "w_released": False,
                "s_pressed": False,
                "s_released": False,
                "space_pressed": False,
                "h_pressed": False,
                "o_pressed": False,
                "shift_j": False,
                "shift_g": False,
                "shift_k": False,
            }

            # Set the singleton instance to self
            Motion.__instance = self

    # Grabs the singleton instance of motion
    @staticmethod
    def get_instance():
        # If the object is not instantiated this will instantiate it.
        if Motion.__instance == None:
            Motion()
        return Motion.__instance

    # Stops a continuoss movement
    def stop_cont_jog(self, motor, move_type: str = "continuous") -> None:
        # Stops the motor
        if move_type == "continuous":
            motor.stop()
        # Sets the movement boolean to false
        if motor == self.x_mot:
            self.x_mot_moving = False
        if motor == self.y_mot:
            self.y_mot_moving = False
        if motor == self.r_mot:
            self.r_mot_moving = False

    # Doesn't work, but is never used, sets the speed of a continuous movement
    def set_velocity(self) -> None:
        # clear()
        os.system("cls")
        velocity = float(input("New velocity (device units):"))
        for m in self.motors:
            m.move_velocity = velocity
        # keyboard.start_recording()

    # Sets the step size of a step movement
    def set_jog_step_linear_input(self) -> None:
        os.system("cls")
        step = float(input("New Jog Step (mm):"))
        self.x_mot.jog_step_size = step
        self.y_mot.jog_step_size = step

    # Sets the step size with a function call
    def set_jog_step_linear(self, step_size: float) -> None:
        self.x_mot.jog_step_size = step_size
        self.y_mot.jog_step_size = step_size

    # Sets the rotational step
    def set_jog_step_rotational(self) -> None:
        os.system("cls")
        step = float(input("New Jog Step (degrees):"))
        self.r_mot.jog_step_size = step

    # Stops All Motors, but then requires K Cubes to be restarted
    def stop_all(self) -> None:
        for m in self.motors:
            m.stop()

    # Does a single Movement using a motor and direction input
    def move_step(self, motor, direction: str) -> None:
        # Checks if it is the x motor and whether the x motor is already moving before moving it
        if motor == self.x_mot:
            if self.x_mot_moving == False:
                motor.jog(direction)
        # Checks if it is the y motor and whether the y motor is already moving before moving it
        if motor == self.y_mot:
            if self.y_mot_moving == False:
                motor.jog(direction)
        # Checks if it is the rotational motor and whether the rotational motor is already moving before moving it
        if motor == self.r_mot:
            if self.r_mot_moving == False:
                motor.jog(direction)
        print(
            "Motor Coordinates: ("
            + str(self.get_x_position())
            + ", "
            + str(self.get_y_position())
            + ")"
        )

    # Performs a continuous movement using a motor and direction input
    def move_cont(self, motor, direction: str) -> None:
        # Checks if it is the x motor and whether the x motor is already moving before moving it
        if motor == self.x_mot:
            if self.x_mot_moving == False:
                motor.move_continuous(direction)
                # sets the movement boolean to true so it will not perform another movement before finishing the current movement
                self.x_mot_moving = True
        # Checks if it is the y motor and whether the y motor is already moving before moving it
        if motor == self.y_mot:
            if self.y_mot_moving == False:
                motor.move_continuous(direction)
                # sets the movement boolean to true so it will not perform another movement before finishing the current movement
                self.y_mot_moving = True
        # Checks if it is the rotational motor and whether the rotational motor is already moving before moving it
        if motor == self.r_mot:
            if self.r_mot_moving == False:
                motor.move_continuous(direction)
                # sets the movement boolean to true so it will not perform another movement before finishing the current movement
                self.r_mot_moving = True

    # Prints the keys and their function
    def help_me(self) -> None:
        global help_txt
        print(help_txt)

    # Set the flag value true
    def set_flag(self, flag: str) -> None:
        self.flags[flag] = True

    # Set the step size flag to true
    def set_flag_lin_step(self) -> None:
        self.flags["shift_j"] = True

    # Set the rotation step size flag to true
    def set_flag_rot_step(self) -> None:
        self.flags["shift_g"] = True

    # Set the velocity speed flag to true
    def set_flag_vel(self) -> None:
        self.flags["shift_k"] = True

    # Resets the motors to base positions
    def home_motors(self) -> None:
        print("Homing motors...")
        self.x_mot.go_home()
        self.y_mot.go_home()
        print("Done homing")

    # Converts GDS coordinates to chip coordinates and goes to those positions
    def go_to_GDS_Coordinates(self, x: float, y: float) -> None:
        # The GDS Coordinates
        gds_pos = np.array([[x], [y], [1]])

        # In case the conversion matrix has not been set
        if self.conversion_matrix is None:
            raise Exception("Set the conversion Matrix before going to GDS coordinates")

        # Calculates the new point and moves to it
        newPoint = self.conversion_matrix @ gds_pos
        self.x_mot.move_to_unblocked(newPoint[0][0])
        self.y_mot.move_to_unblocked(newPoint[1][0])

    # Will go to GDS y position entered in
    def go_to_GDS_Coordinates_y(self, y_pos: float = None) -> None:
        if y_pos == None:
            y_pos = float(input("Enter in Y Coordinate (mm): "))
        # The GDS Coordinates
        gds_pos = np.array([[self.get_x_position()], [y_pos], [1]])

        # In case the conversion matrix has not been set
        if self.conversion_matrix is None:
            raise Exception("Set the conversion Matrix before going to GDS coordinates")

        # Calculates the new point and moves to it
        newPoint = self.conversion_matrix @ gds_pos
        self.y_mot.move_to(newPoint[1][0])

    # Will go to GDS x position entered in
    def go_to_GDS_Coordinates_x(self, x_pos: float = None) -> None:
        if x_pos == None:
            x_pos = float(input("Enter in X Coordinate (mm): "))
        # The GDS Coordinates
        gds_pos = np.array([[x_pos], [self.get_y_position()], [1]])

        # In case the conversion matrix has not been set
        if self.conversion_matrix is None:
            raise Exception("Set the conversion Matrix before going to GDS coordinates")

        # Calculates the new point and moves to it
        newPoint = self.conversion_matrix @ gds_pos
        self.x_mot.move_to(newPoint[0][0])

    # Goes to Chip Coordinates, which are more undefined
    def go_to_chip_coordinates(self, x: float, y: float) -> None:
        self.x_mot.move_to_unblocked(x)
        self.y_mot.move_to_unblocked(y)

    # Goes to the Chip y coordinate entered in
    def go_to_chip_coordinates_y(self, y: float) -> None:
        self.y_mot.move_to(y)

    # Goes the the Chip x coordinate entered in
    def go_to_chip_coordinates_x(self, x: float) -> None:
        self.x_mot.move_to(x)

    # Goes to the position attributed to the circuit parameter
    def go_to_circuit(self, circuit: map.Circuit) -> None:
        pos = circuit.location
        try:
            self.go_to_GDS_Coordinates(float(pos[0]), float(pos[1]))
        except Exception as e:
            print("Error: Tried to call go_to_GDS_Coordinates()\n" + str(e))

    # Get the y position of the y motor
    def get_y_position(self) -> float:
        return self.y_mot.get_position()

    # Get the x position of motor x
    def get_x_position(self) -> float:
        return self.x_mot.get_position()

    # Get the rotation of the motor r
    def get_r_position(self) -> float:
        return self.r_mot.get_position()

    def rotate_conversion_matrix(self, direction: str = "forward") -> None:
        # This is more for debugging, but it holds the x and y positions of the motors at the current viewing location
        point = [self.get_x_position(), self.get_y_position()]
        # This is the point in reference to the calibrated origin
        original_point = np.array(
            [[point[0] - self.origin[0]], [point[1] - self.origin[1]],]
        )

        # Converts degrees to radians and determines the direction of the rotation
        theta = math.radians(self.r_mot.jog_step_size)
        sign = 1 if direction == "forward" else -1

        # The rotation matrix, which will predict the new location
        rotation_matrix = np.array(
            [
                [math.cos(theta), sign * math.sin(theta),],
                [-sign * math.sin(theta), math.cos(theta),],
            ]
        )

        # Get the calibration from the data cache and then get the points
        calibration = DataCache.get_instance().get_calibration()
        point1, point2, point3 = calibration.get_points()

        # Calculate the new points
        new_point1 = rotation_matrix @ point1
        new_point2 = rotation_matrix @ point2
        new_point3 = rotation_matrix @ point3

        # Get the new conversion matrix, which automatically sets the conversion matrix in motion
        calibration.calculate_conversion_matrix(new_point1, new_point2, new_point3)

    # Performs a continuos concentric rotation to keep the same center over the microscope
    def unblocked_rotation(
        self, direction: str = "forward", angle: float = None
    ) -> None:
        # Default angle change
        if angle == None:
            angle = self.r_mot.jog_step_size
        # This is more for debugging, but it holds the x and y positions of the motors at the current viewing location
        point = [self.get_x_position(), self.get_y_position()]
        # This is the point in reference to the calibrated origin
        original_point = np.array(
            [[point[0] - self.origin[0]], [point[1] - self.origin[1]],]
        )

        # Converts degrees to radians and determines the direction of the rotation
        theta = math.radians(angle)
        sign = 1 if direction == "forward" else -1

        # The rotation matrix, which will predict the new location
        rotation_matrix = np.array(
            [
                [math.cos(theta), sign * math.sin(theta),],
                [-sign * math.sin(theta), math.cos(theta),],
            ]
        )

        # The Next Point is calculated by matrix multiplying the rotation matrix by the point in reference to the calibrated origin
        new_point = rotation_matrix @ original_point

        # The new Motor Coordinates
        x_pos = new_point[0][0] + self.origin[0]
        y_pos = new_point[1][0] + self.origin[1]

        original_angle = self.r_mot.jog_step_size
        self.r_mot.jog_step_size = angle

        # Will move the motors without a blocking function
        self.x_mot.move_to_unblocked(x_pos)
        self.y_mot.move_to_unblocked(y_pos)
        self.move_step(self.r_mot, direction)

        self.rotate_conversion_matrix(direction)
        self.r_mot.jog_step_size = original_angle

    # Performs a rotation where you return to the spot you were looking at post rotation
    def concentric_rotatation(
        self, direction: str = "forward", angle: float = None
    ) -> None:
        # Default angle change
        if angle == None:
            angle = self.r_mot.jog_step_size
        # This is more for debugging, but it holds the x and y positions of the motors at the current viewing location
        point = [self.get_x_position(), self.get_y_position()]
        # This is the point in reference to the calibrated origin
        original_point = np.array(
            [[point[0] - self.origin[0]], [point[1] - self.origin[1]],]
        )

        # Converts degrees to radians and determines the direction of the rotation
        theta = math.radians(angle)
        sign = 1 if direction == "forward" else -1

        # The rotation matrix, which will predict the new location
        rotation_matrix = np.array(
            [
                [math.cos(theta), sign * math.sin(theta),],
                [-sign * math.sin(theta), math.cos(theta),],
            ]
        )

        # The Next Point is calculated by matrix multiplying the rotation matrix by the point in reference to the calibrated origin
        new_point = rotation_matrix @ original_point

        # The new Motor Coordinates
        x_pos = new_point[0][0] + self.origin[0]
        y_pos = new_point[1][0] + self.origin[1]

        print("x motor moving...")
        self.x_mot.move_to(x_pos)
        print("y motor moving...")
        self.y_mot.move_to(y_pos)
        original_angle = self.r_mot.jog_step_size
        self.r_mot.jog_step_size = angle
        print("r motor moving...")
        self.move_step(self.r_mot, direction)
        print("Rotating Matrix...")
        self.rotate_conversion_matrix(direction)
        self.r_mot.jog_step_size = original_angle

    # Will go to x position entered in
    def set_rotation(self, r_pos: float = None) -> None:
        if r_pos == None:
            r_pos = float(input("Enter in Rotation (deg): "))
        self.r_mot.move_to(r_pos)

    # Set the conversion matrix
    def set_conversion_matrix(self, matrix: np.numarray) -> None:
        self.conversion_matrix = matrix

    # Set the origin
    def set_origin(self, origin: list) -> None:
        self.origin = origin

    # Prints the Current GDS Coordinate
    def print_GDS_position(self) -> None:
        # Get the Motor Coordinates
        motor_coordinate_x = self.get_x_position()
        motor_coordinate_y = self.get_y_position()
        motor_coordinate = np.array([[motor_coordinate_x], [motor_coordinate_y], [1]])

        # Invert Conversion Matrix to convert from Motor to GDS, instead of GDS to Motor
        # Matrix Multiply New Matrix with Motor Coordinates to get GDS Coordinates
        gds_coordinate = np.linalg.inv(self.conversion_matrix) @ motor_coordinate
        print(
            "GDS Coordinate: ("
            + str(gds_coordinate[0][0])
            + ", "
            + str(gds_coordinate[1][0])
            + ")"
        )

        def set_conversion_matrix_rotation_variables(
            self, gds_matrix, point1, point2, point3
        ) -> None:
            self.gds_matrix = gds_matrix
            self.point1 = point1
            self.point2 = point2
            self.point3 = point3

