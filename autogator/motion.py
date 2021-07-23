# -*- coding: utf-8 -*-
#
# Copyright © Autogator Project Contributors
# Licensed under the terms of the GNU GPLv3+ License
# (see autogator/__init__.py for details)

"""
Motion Class
-------------------------------------

Instructs movement of motors.
"""

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

        try:
            for motor in self.motors:
                motor.autoconnect()
        except:
            self.x_mot.connect(serialno=27504851)
            self.y_mot.connect(serialno=27003497)
            self.r_mot.connect(serialno=27003366)

        self.conversion_matrix = conversion_matrix
        self.origin = None

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
            "shift_g": False,
        }

    def stop_motion(self, motor, move_type: str = "continuous") -> None:
        """
        Stops motor motion is it is moving conintuously and marks motor as not moving.

        Parameters
        ----------
        motor : Z825B
            Which motor needs to be stopped and marked not moving.
        move_type : str
            Whether the motor is currently moving continuously or stepped.
        """
        if move_type != "continuous":
            return
        if motor == self.x_mot and self.x_mot_moving:
            self.x_mot_moving = False
            motor.stop()
        if motor == self.y_mot and self.y_mot_moving:
            self.y_mot_moving = False
            motor.stop()
        if motor == self.r_mot and self.r_mot_moving:
            self.r_mot_moving = False
            motor.stop()

    def set_jog_step_linear(self, step_size: float = None) -> None:
        """
        Sets jog step of linear motors.

        .. note:: Asks for user input if step_size isn't provided in function call.

        Parameters
        ----------
        step_size : float, default=None
            New jog step size for linear motors.
        """
        if step_size is None:
            os.system("cls")
            step_size = float(input("New Jog Step (mm):"))
        self.x_mot.jog_step_size = step_size
        self.y_mot.jog_step_size = step_size

    def get_jog_step_linear(self) -> float:
        """
        Returns the jog step size of the linear motors.

        Returns
        -------
        jog_step_size : float
            Current jog step size of linear motors.
        """
        return self.x_mot.jog_step_size

    def set_jog_step_rotational(self, step_size: float = None) -> None:
        """
        Sets jog step of rotational motor.

        .. note:: Asks for user input if step_size isn't provided in function call.

        Parameters
        ----------
        step_size : float, default=None
            New jog step size for rotational motor.
        """
        if step_size is None:
            os.system("cls")
            step_size = float(input("New Jog Step (degrees):"))
        self.r_mot.jog_step_size = step_size

    def get_jog_step_rotational(self) -> float:
        """
        Returns the jog step size of the rotational motor.

        Returns
        -------
        jog_step_size : float
            Current jog step size of rotational motor.
        """
        return self.r_mot.jog_step_size

    def stop_all(self) -> None:
        """
        Stops all motors from moving

        .. note:: Requires K-Cubes to be manually restarted after called.
        """
        for m in self.motors:
            m.stop()

    def move_step(self, motor, direction: str) -> None:
        """
        Moves a motor one jog based on current jog step size.

        .. note:: Motor must not be currently moving for function to be called.

        Parameters
        ----------
        motor : Z825B
            The motor that will move one jog.
        direction : str
            The direction the motor will move (Must be "forward" or "backward").
        """
        if motor == self.x_mot:
            if self.x_mot_moving == False:
                motor.jog(direction)
        if motor == self.y_mot:
            if self.y_mot_moving == False:
                motor.jog(direction)
        if motor == self.r_mot:
            if self.r_mot_moving == False:
                motor.jog(direction)

    def move_cont(self, motor, direction: str) -> None:
        """
        Starts a continuous movement of a motor and marks it as currently moving.

        Parameters
        ----------
        motor : Z825B
            The motor that will move.
        direction : str
            The direction the motor will move (Must be "forward" or "backward").
        """
        if motor == self.x_mot:
            if self.x_mot_moving == False:
                motor.move_continuous(direction)
                self.x_mot_moving = True
        if motor == self.y_mot:
            if self.y_mot_moving == False:
                motor.move_continuous(direction)
                self.y_mot_moving = True
        if motor == self.r_mot:
            if self.r_mot_moving == False:
                motor.move_continuous(direction)
                self.r_mot_moving = True

    def help_me(self) -> None:
        """
        Prints help text to terminal to inform user of commands available.
        """
        global help_txt
        print(help_txt)

    def set_flag(self, flag: str) -> None:
        """
        Sets a flags value to True

        Parameters
        ----------
        flag : str
            Flag to be set to True.
        """
        self.flags[flag] = True

    def set_flag_lin_step(self) -> None:
        """
        Sets a linear step flag value to True

        .. note:: Seperate function from set_flag() because "shift + button" commands are called differently.
        """
        self.flags["shift_j"] = True

    def set_flag_rot_step(self) -> None:
        """
        Sets a rotational step flag value to True

        .. note:: Seperate function from set_flag() because "shift + button" commands are called differently.
        """
        self.flags["shift_g"] = True

    def home_motors(self) -> None:
        """
        Moves linear motors to home position.
        """
        print("Homing motors...")
        self.x_mot.go_home()
        self.y_mot.go_home()
        print("Done homing")

    def go_to_gds_coordinates(self, x: float = None, y: float = None) -> None:
        """
        Converts GDS coordinates to stage coordinates and moves to position.

        .. note:: If x or y variable isn't passed it will only move to positions given.

        Parameters
        ----------
        x : float, default=None
            x part of GDS coordinate to go to.
        y : float, default=None
            y part of GDS coordinate to go to.

        Raises
        ------
        Exception
            If conversion matrix is null it cannot calculate the stage coordinates.
        """
        go_to_x = True
        go_to_y = True

        if x is None:
            x = 0.0
            go_to_x = False
        if y is None:
            y = 0.0
            go_to_y = False
        gds_pos = np.array([[x], [y], [1]])

        if self.conversion_matrix is None:
            raise Exception("Set the conversion Matrix before going to GDS coordinates")

        newPoint = self.conversion_matrix @ gds_pos
        if go_to_x:
            self.x_mot.move_to(newPoint[0][0])
        if go_to_y:
            self.y_mot.move_to(newPoint[1][0])

    def go_to_stage_coordinates(self, x: float = None, y: float = None) -> None:
        """
        Goes to stage coordinates provided.

        .. note:: If x or y variable isn't passed it will only move to positions given.

        Parameters
        ----------
        x : float, default=None
            x part of stage coordinate to go to.
        y : float, default=None
            y part of stage coordinate to go to.
        """
        if x is not None:
            self.x_mot.move_to(x)
        if y is not None:
            self.y_mot.move_to(y)

    def go_to_circuit(self, circuit) -> None:
        """
        Retrievs GDS location for circuit object and uses go_to_gds_coordinates() to go to it.

        Parameters
        ----------
        circuit : Circuit
            Circuit object to go to.

        Raises
        ------
        Exception
            If an error occurs while trying to run go_to_gsd_coordinates() on location retrieved.
        """
        pos = circuit.location
        try:
            self.go_to_gds_coordinates(float(pos[0]), float(pos[1]))
        except Exception as e:
            print("Error: Tried to call go_to_gds_coordinates()\n" + str(e))

    def get_motor_position(self, motor) -> float:
        """
        Returns stage coordinates of a motor's current position.

        Parameters
        ----------
        motor : Z825B
            The motor who's position is being returned.

        Returns
        -------
        motor_position : float
            Stage coordinate of motor position.
        """
        return motor.get_position()

    # Performs a rotation where you return to the spot you were looking at post rotation (don't know if works)
    def concentric_rotatation(self, direction: str = "forward") -> None:
        original_point = np.array(
            [
                [self.get_motor_position(self.x_mot) - self.origin[0]],
                [self.get_motor_position(self.y_mot) - self.origin[1]],
            ]
        )

        print("Step Size is " + str(self.r_mot.jog_step_size))

        theta = math.radians(self.r_mot.jog_step_size)
        sign = 1 if direction == "forward" else -1
        rotation_matrix = np.array(
            [
                [
                    math.cos(theta),
                    sign * math.sin(theta),
                ],
                [
                    -sign * math.sin(theta),
                    math.cos(theta),
                ],
            ]
        )

        new_point = rotation_matrix @ original_point

        self.move_step(self.r_mot, direction)
        print(original_point)
        print()
        print(rotation_matrix)
        print()
        print(new_point)

        delta_x = -original_point[0][0] + new_point[0][0]
        delta_y = -original_point[1][0] + new_point[1][0]
        x_pos = original_point[0][0] - delta_x + self.origin[0]
        y_pos = original_point[1][0] + (delta_y / 2.0) + self.origin[1]
        self.x_mot.move_to(x_pos)
        self.y_mot.move_to(y_pos)

    # Will go to x position entered in (don't know if works)
    def rotate_to_position(self, r_pos: float = None) -> None:
        if r_pos == None:
            r_pos = float(input("Enter in Rotation (deg): "))
        self.r_mot.move_to(r_pos)

    def keyloop(self, quit_key="q"):
        """
        Starts keyboard logic that controls the motors through key presses.

        .. note:: Refer to help_txt for command information

        Parameters
        ----------
        quit_key = char, default='q'
            The character refering to which key being pressed will quit the keyloop.
        """
        keyboard.on_press_key(
            "left arrow", lambda _: self.set_flag("left_arrow_pressed")
        )
        keyboard.on_release_key(
            "left arrow", lambda _: self.set_flag("left_arrow_released")
        )
        keyboard.on_press_key(
            "right arrow", lambda _: self.set_flag("right_arrow_pressed")
        )
        keyboard.on_release_key(
            "right arrow", lambda _: self.set_flag("right_arrow_released")
        )
        keyboard.on_press_key("up arrow", lambda _: self.set_flag("up_arrow_pressed"))
        keyboard.on_release_key(
            "up arrow", lambda _: self.set_flag("up_arrow_released")
        )
        keyboard.on_press_key(
            "down arrow", lambda _: self.set_flag("down_arrow_pressed")
        )
        keyboard.on_release_key(
            "down arrow", lambda _: self.set_flag("down_arrow_released")
        )
        keyboard.on_press_key("c", lambda _: self.set_flag("c_pressed"))
        keyboard.on_release_key("c", lambda _: self.set_flag("c_released"))
        keyboard.on_press_key("x", lambda _: self.set_flag("x_pressed"))
        keyboard.on_release_key("x", lambda _: self.set_flag("x_released"))
        keyboard.on_press_key("a", lambda _: self.set_flag("a_pressed"))
        keyboard.on_release_key("a", lambda _: self.set_flag("a_released"))
        keyboard.on_press_key("d", lambda _: self.set_flag("d_pressed"))
        keyboard.on_release_key("d", lambda _: self.set_flag("d_released"))
        keyboard.on_press_key("w", lambda _: self.set_flag("w_pressed"))
        keyboard.on_release_key("w", lambda _: self.set_flag("w_released"))
        keyboard.on_press_key("s", lambda _: self.set_flag("s_pressed"))
        keyboard.on_release_key("s", lambda _: self.set_flag("s_released"))
        keyboard.add_hotkey("shift + j", self.set_flag_lin_step)
        keyboard.add_hotkey("shift + g", self.set_flag_rot_step)
        keyboard.on_press_key("space", lambda _: self.set_flag("space_pressed"))
        keyboard.on_press_key("h", lambda _: self.set_flag("h_pressed"))
        keyboard.on_press_key("o", lambda _: self.set_flag("o_pressed"))

        print(help_txt)

        while True:
            if keyboard.is_pressed(quit_key):
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
