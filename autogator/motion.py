from ctypes import c_int, c_double, byref, pointer
import numpy as np
import time
import keyboard
import os
import math

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
    \tspacebar - emergency stop all
    \to - home linear motors
    \th - help
    \tq - quit
    """

class Motion:
    def __init__(self, x_mot, y_mot, r_mot, conversion_matrix=None):
        self.x_mot = x_mot
        self.y_mot = y_mot
        self.r_mot = r_mot
        self.motors = [self.x_mot, self.y_mot, self.r_mot]

        for motor in self.motors:
            motor.autoconnect()

        self.conversion_matrix = conversion_matrix
        # self.origin = None

        # Sets these to false so that motors can move without intereference
        self.x_mot_moving = False
        self.y_mot_moving = False
        self.r_mot_moving = False

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
            "shift_g": False
        }

    # Stops a continuos movement
    def stop_motion(self, motor, move_type: str = "continuous") -> None:
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

    # Sets the step size with a function call
    def set_jog_step_linear(self, step_size: float = None) -> None:
        if step_size is None:
            os.system("cls")
            step_size = float(input("New Jog Step (mm):"))
        self.x_mot.jog_step_size = step_size
        self.y_mot.jog_step_size = step_size

    # Returns the step size with a function call
    def get_jog_step_linear(self) -> float:
        return self.x_mot.jog_step_size

    # Sets the rotational step
    def set_jog_step_rotational(self, step_size: float=None) -> None:
        if step_size is None:
            os.system("cls")
            step_size = float(input("New Jog Step (degrees):"))
        self.r_mot.jog_step_size = step_size

    # Returns the step size with a function call
    def get_jog_step_rotational(self) -> float:
        return self.r_mot.jog_step_size

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

    # Resets the motors to base positions
    def home_motors(self) -> None:
        print("Homing motors...")
        self.x_mot.go_home()
        self.y_mot.go_home()
        print("Done homing")

    # Converts GDS coordinates to chip coordinates and goes to those positions
    def go_to_gds_coordinates(self, x: float=None, y: float=None) -> None:
        go_to_x = True
        go_to_y = True

        if x is None:
            x = 0.0
            go_to_x = False
        if y is None:
            y = 0.0
            go_to_y = False
        gds_pos = np.array([[x], [y], [1]])

        # Throws exception if the conversion matrix has not been set
        if self.conversion_matrix is None:
            raise Exception("Set the conversion Matrix before going to GDS coordinates")

        # Calculates the new point and moves to it
        newPoint = self.conversion_matrix @ gds_pos
        if go_to_x:
            self.x_mot.move_to(newPoint[0][0])
        if go_to_y:
            self.y_mot.move_to(newPoint[1][0])

    # Goes to Chip Coordinates, which are more undefined
    def go_to_stage_coordinates(self, x: float=None, y: float=None) -> None:
        if x is not None:
            self.x_mot.move_to(x)
        if y is not None:
            self.y_mot.move_to(y)

    # Goes to the position attributed to the circuit parameter
    def go_to_circuit(self, circuit) -> None:
        pos = circuit.location
        try:
            self.go_to_gds_coordinates(float(pos[0]), float(pos[1]))
        except Exception as e:
            print("Error: Tried to call go_to_gds_coordinates()\n" + str(e))

    # Get the position of a motor
    def get_motor_position(self, motor) -> float:
        return motor.get_position()

    # Performs a rotation where you return to the spot you were looking at post rotation
    # def concentric_rotatation(self, direction: str = "forward") -> None:
    #     original_point = np.array(
    #         [
    #             [self.get_motor_position(self.x_mot) - self.origin[0]],
    #             [self.get_motor_position(self.y_mot) - self.origin[1]],
    #         ]
    #     )

    #     print("Step Size is " + str(self.r_mot.jog_step_size))

    #     theta = math.radians(self.r_mot.jog_step_size)
    #     sign = 1 if direction == "forward" else -1
    #     rotation_matrix = np.array(
    #         [
    #             [
    #                 math.cos(theta),
    #                 sign * math.sin(theta),
    #             ],
    #             [
    #                 -sign * math.sin(theta),
    #                 math.cos(theta),
    #             ],
    #         ]
    #     )

    #     new_point = rotation_matrix @ original_point

    #     self.move_step(self.r_mot, direction)
    #     print(original_point)
    #     print()
    #     print(rotation_matrix)
    #     print()
    #     print(new_point)

    #     delta_x = -original_point[0][0] + new_point[0][0]
    #     delta_y = -original_point[1][0] + new_point[1][0]
    #     x_pos = original_point[0][0] - delta_x + self.origin[0]
    #     y_pos = original_point[1][0] + (delta_y / 2.0) + self.origin[1]
    #     self.x_mot.move_to(x_pos)
    #     self.y_mot.move_to(y_pos)

    # Will go to x position entered in
    def rotate_to_position(self, r_pos: float=None) -> None:
        if r_pos == None:
            r_pos = float(input("Enter in Rotation (deg): "))
        self.r_mot.move_to(r_pos)

    # Set the conversion matrix
    def set_conversion_matrix(self, matrix: np.numarray) -> None:
        self.conversion_matrix = matrix

    # Set the origin
    def set_origin(self, origin: list) -> None:
        self.origin = origin.bumpversion.cfg

    def keyloop(self,quitKey = 'q'):
        keyboard.on_press_key('left arrow', lambda _:self.set_flag('left_arrow_pressed'))
        keyboard.on_release_key('left arrow', lambda _:self.set_flag('left_arrow_released'))
        keyboard.on_press_key('right arrow', lambda _:self.set_flag('right_arrow_pressed'))
        keyboard.on_release_key('right arrow', lambda _:self.set_flag('right_arrow_released'))
        keyboard.on_press_key('up arrow', lambda _:self.set_flag('up_arrow_pressed'))
        keyboard.on_release_key('up arrow', lambda _:self.set_flag('up_arrow_released'))
        keyboard.on_press_key('down arrow', lambda _:self.set_flag('down_arrow_pressed'))
        keyboard.on_release_key('down arrow', lambda _:self.set_flag('down_arrow_released'))
        keyboard.on_press_key('c', lambda _:self.set_flag('c_pressed'))
        keyboard.on_release_key('c', lambda _:self.set_flag('c_released'))
        keyboard.on_press_key('x', lambda _:self.set_flag('x_pressed'))
        keyboard.on_release_key('x', lambda _:self.set_flag('x_released'))
        keyboard.on_press_key('a', lambda _:self.set_flag('a_pressed'))
        keyboard.on_release_key('a', lambda _:self.set_flag("a_released"))
        keyboard.on_press_key('d', lambda _:self.set_flag("d_pressed"))
        keyboard.on_release_key('d', lambda _:self.set_flag("d_released"))
        keyboard.on_press_key('w', lambda _:self.set_flag("w_pressed"))
        keyboard.on_release_key('w', lambda _:self.set_flag("w_released"))
        keyboard.on_press_key('s', lambda _:self.set_flag("s_pressed"))
        keyboard.on_release_key('s', lambda _:self.set_flag("s_released"))
        keyboard.add_hotkey('shift + j', self.set_flag_lin_step)
        keyboard.add_hotkey('shift + g', self.set_flag_rot_step)      
        keyboard.on_press_key('space', lambda _:self.set_flag("space_pressed"))
        keyboard.on_press_key('h', lambda _:self.set_flag("h_pressed"))
        keyboard.on_press_key('o', lambda _:self.set_flag("o_pressed"))

        print(help_txt)

        while True:
            if keyboard.is_pressed(quitKey):
                print("QUIT")
                os.system("cls")
                break
            for flag in self.flags:
                if self.flags[flag]:
                    if flag == "left_arrow_pressed":
                        self.move_step(self.x_mot, "backward")
                    elif flag == "left_arrow_released":
                        self.stop_motion(self.x_mot, "step")
                    elif flag == "right_arrow_pressed":
                        self.move_step(self.x_mot, "forward")
                    elif flag == "right_arrow_released":
                        self.stop_motion(self.x_mot, "step")
                    elif flag == "up_arrow_pressed":
                        self.move_step(self.y_mot, "forward")
                    elif flag == "up_arrow_released":
                        self.stop_motion(self.y_mot, "step")
                    elif flag == "down_arrow_pressed":
                        self.move_step(self.y_mot, "backward")
                    elif flag == "down_arrow_released":
                        self.stop_motion(self.y_mot, "step")
                    elif flag == "c_pressed":
                        self.move_step(self.r_mot, "forward")
                    elif flag == "c_released":
                        self.stop_motion(self.r_mot, "step")
                    elif flag == "x_pressed":
                        self.move_step(self.r_mot, "backward")
                    elif flag == "x_released":
                        self.stop_motion(self.r_mot, "step")
                    elif flag == "a_pressed":
                        self.move_cont(self.x_mot, "backward")
                    elif flag == "a_released":
                        self.stop_motion(self.x_mot, "continuous")
                    elif flag == "d_pressed":
                        self.move_cont(self.x_mot, "forward")
                    elif flag == "d_released":
                        self.stop_motion(self.x_mot, "continuous")
                    elif flag == "w_pressed":
                        self.move_cont(self.y_mot, "forward")
                    elif flag == "w_released":
                        self.stop_motion(self.y_mot, "continuous")
                    elif flag == "s_pressed":
                        self.move_cont(self.y_mot, "backward")
                    elif flag == "s_released":
                        self.stop_motion(self.y_mot, "continuous")
                    elif flag == "space_pressed":
                        self.stop_all()
                    elif flag == "h_pressed":
                        self.help_me()
                    elif flag == "o_pressed":
                        self.home_motors()
                    elif flag == "shift_j":
                        self.set_jog_step_linear()
                    elif flag == "shift_g":
                        self.set_jog_step_rotational()
                    
                    self.flags[flag] = False
