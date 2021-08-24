# -*- coding: utf-8 -*-
#
# Copyright © Autogator Project Contributors
# Licensed under the terms of the MIT License
# (see autogator/__init__.py for details)

"""
Data Scanner
------------

Optimizes alignment of laser through box scans.
"""

import time
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


class DataScanner:
    def __init__(
        self,
        oscilloscope,
        motion,
        channel=1,
        channel_range=5.5,
        coupling="DCLimit",
        position=-5.0,
    ):
        self.oscope = oscilloscope
        self.motion = motion
        self.oscope.set_channel_for_measurement(
            channel=channel,
            range=channel_range,
            coupling=coupling,
            position=position,
            timescale=1e-9,
        )

    def auto_scan(self, channel=1):
        """
        Performs large basic box scan to find general area of optimal alignment, then moves in y direction until max is found and returns to it. Repeats with X direction.
        """
        self.basic_scan(sweep_distance=0.025, step_size=0.005, channel=channel)
        print("Max Data Reading: {}".format(self.oscope.measure()))
        print(
            "Max Data Location: ({}, {})".format(
                self.motion.get_motor_position(self.motion.x_mot),
                self.motion.get_motor_position(self.motion.y_mot),
            )
        )
        y_max_location = self.anti_backlash_scan(self.motion.y_mot)
        x_max_location = self.anti_backlash_scan(self.motion.x_mot)
        self.motion.go_to_stage_coordinates(x_max_location, y_max_location)
        print("Max Data Reading: {}".format(self.oscope.measure()))
        print(
            "Max Data Location: ({}, {})".format(
                self.motion.get_motor_position(self.motion.x_mot),
                self.motion.get_motor_position(self.motion.y_mot),
            )
        )

    def basic_scan(
        self,
        sweep_distance,
        step_size,
        plot=False,
        sleep_time=0.5,
        channel=1,
        channel_range=5.5,
        coupling="DCLimit",
        position=-5.0,
    ):
        """
        Performs a box scan of given dimensions and goes to position of highest readings returned.

        Parameters
        ----------
        sweep_distance : float
            Length of one side of the square the box scan spans.
        step_size : float
            Jog step size motors will use when iterating through the box.
        plot : Bool, default=False
            If a visible plot is generated displaying data returned from scan.
        sleep_time : float, default=.2
            Amount of time in seconds the motors will pause inbetween movements to improve data reliability.
        channel : int, default=1
            Channel used on the oscilliscope to return readings.
        channel_range : float, default=5.5
            Range used for the channel on the oscilliscope that will return readings.
        coupling : str, default="DCLimit"
            Type of coupling used for the channel on the oscilliscope that will return readings.
        position: float, default=-5.0
            Position of Oscilliscope screen relative to zero when displaying readings.
        """

        self.oscope.set_channel(
            channel, range=channel_range, coupling=coupling, position=position
        )
        self.oscope.set_auto_measurement(source="C" + str(channel) + "W1")
        self.oscope.wait_for_device()

        x_start_place = self.motion.get_motor_position(self.motion.x_mot) - (
            sweep_distance / 2.0
        )
        y_start_place = self.motion.get_motor_position(self.motion.y_mot) - (
            sweep_distance / 2.0
        )
        self.motion.go_to_stage_coordinates(x=x_start_place, y=y_start_place)
        time.sleep(sleep_time)

        max_data = self.oscope.measure()
        max_data_loc = [x_start_place, y_start_place]

        self.motion.set_jog_step_linear(step_size)

        edge_num = round(sweep_distance / step_size)
        data = np.zeros((edge_num, edge_num))
        rows, cols = data.shape

        if plot:
            fig, ax = plt.subplots(1, 1)
            im = ax.imshow(data, cmap="hot")

        moving_down = False

        for i in range(rows):
            for j in range(cols):
                data[i, j] = self.oscope.measure()
                print(data[i, j])
                print(
                    "({}, {})".format(
                        self.motion.get_motor_position(self.motion.x_mot),
                        self.motion.get_motor_position(self.motion.y_mot),
                    )
                )
                if data[i, j] > max_data:
                    max_data = data[i, j]
                    max_data_loc = [
                        self.motion.get_motor_position(self.motion.x_mot),
                        self.motion.get_motor_position(self.motion.y_mot),
                    ]

                self.motion.move_step(self.motion.y_mot, "forward")
                time.sleep(sleep_time)

                if plot:
                    im.set_data(data)
                    im.set_clim(data.min(), data.max())
                    fig.canvas.draw_idle()
                    plt.pause(0.000001)

            self.motion.go_to_stage_coordinates(y=y_start_place)
            self.motion.move_step(self.motion.x_mot, "forward")

            time.sleep(sleep_time)

        self.motion.go_to_stage_coordinates(
            float(max_data_loc[0]), float(max_data_loc[1])
        )
        time.sleep(sleep_time)
        if plot:
            plt.show()

    def basic_scan_rect(
        self,
        sweep_distance_x,
        sweep_distance_y,
        step_size_x,
        step_size_y,
        plot=False,
        sleep_time=0.2,
        channel=1,
        channel_range=5.5,
        coupling="DCLimit",
        position=-5.0,
    ):
        """
        Performs a rectangle scan of given dimensions and goes to position of highest readings returned.

        Parameters
        ----------
        sweep_distance_x : float
            Length of x side of the rectangle the box scan spans.
        sweep_distance_y : float
            Length of y side of the rectangle the box scan spans.
        step_size_x : float
            Jog step size x motor will use when iterating through the box.
        step_size_y : float
            Jog step size y motor will use when iterating through the box.
        plot : Bool, default=False
            If a visible plot is generated displaying data returned from scan.
        sleep_time : float, default=.2
            Amount of time in seconds the motors will pause inbetween movements to improve data reliability.
        channel : int, default=1
            Channel used on the oscilliscope to return readings.
        channel_range : float, default=5.5
            Range used for the channel on the oscilliscope that will return readings.
        coupling : str, default="DCLimit"
            Type of coupling used for the channel on the oscilliscope that will return readings.
        position: float, default=-5.0
            Position of Oscilliscope screen relative to zero when displaying readings.
        """

        self.oscope.set_channel(
            channel, range=channel_range, coupling=coupling, position=position
        )
        self.oscope.set_auto_measurement(source="C" + str(channel) + "W1")
        self.oscope.wait_for_device()

        x_start_place = self.motion.get_motor_position(self.motion.x_mot) - (
            sweep_distance_x / 2.0
        )
        y_start_place = self.motion.get_motor_position(self.motion.y_mot) - (
            sweep_distance_y / 2.0
        )
        self.motion.go_to_stage_coordinates(x_start_place, y_start_place)
        time.sleep(sleep_time)

        max_data = self.oscope.measure()
        max_data_loc = [x_start_place, y_start_place]

        edge_num_x = round(sweep_distance_x / step_size_x)
        edge_num_y = round(sweep_distance_y / step_size_y)
        data = np.zeros((edge_num_x, edge_num_y))
        rows, cols = data.shape

        if plot:
            fig, ax = plt.subplots(1, 1)
            im = ax.imshow(data, cmap="hot")

        moving_down = False

        for i in range(rows):
            for j in range(cols):
                self.motion.set_jog_step_linear(step_size_y)
                data[i, j] = self.oscope.measure()
                print(data[i, j])
                if data[i, j] > max_data:
                    max_data = data[i, j]
                    max_data_loc = [
                        self.motion.get_motor_position(self.motion.x_mot),
                        self.motion.get_motor_position(self.motion.y_mot),
                    ]

                if moving_down:
                    self.motion.move_step(self.motion.y_mot, "backward")
                    time.sleep(sleep_time)
                else:
                    self.motion.move_step(self.motion.y_mot, "forward")
                    time.sleep(sleep_time)

                if plot:
                    im.set_data(data)
                    im.set_clim(data.min(), data.max())
                    fig.canvas.draw_idle()
                    plt.pause(0.000001)

            if moving_down:
                moving_down = False
            else:
                moving_down = True
            self.motion.set_jog_step_linear(step_size_x)
            self.motion.move_step(self.motion.x_mot, "forward")
            time.sleep(sleep_time)

        self.motion.go_to_stage_coordinates(
            float(max_data_loc[0]), float(max_data_loc[1])
        )
        time.sleep(sleep_time)
        if plot:
            plt.show()

    def anti_backlash_scan(self, motor):
        """
        Goes forward direction of motor recording data while it moves. Returns to max data location when determined it has been passed.

        Parameters
        ----------
        motor: Z825BLinearMotor
            Motor that will be moved to find max data location.

        Returns
        -------
        max_data_location: float
            Stage coordinate of location found to return the max data point.
        """
        motor.jog_step_size = 0.0025
        motor.jog("backward")
        motor.jog_step_size = 0.0005
        max_data = self.oscope.measure()
        max_data_location = motor.get_position()
        count = 0
        while count < 12:
            motor.jog("forward")
            time.sleep(0.5)
            data = self.oscope.measure()
            location = motor.get_position()
            print(data)
            print(location)
            if data > max_data:
                count = 0
                max_data = data
                max_data_location = location
            else:
                count += 1
        motor.move_to(max_data_location)
        return max_data_location
