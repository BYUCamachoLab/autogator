# -*- coding: utf-8 -*-
#
# Copyright © Autogator Project Contributors
# Licensed under the terms of the GNU GPLv3+ License
# (see autogator/__init__.py for details)

"""
DataScanner Class
-------------------------------------

Optimizes alignment of laser through box scans.
"""

import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import time

class DataScanner:
    def __init__(self, oscilloscope, motion, channel=1):
        self.oscope = oscilloscope
        self.motion = motion
        self.oscope.set_timescale(1e-9)
        self.oscope.set_channel(channel, range=5.5, coupling="DCLimit", position=-5)
        self.oscope.set_auto_measurement()
        self.oscope.wait_for_device()

    def auto_scan(self):
        """
        Performs basic scans of varying sizes to find location where highest readings are returned.
        """
        self.basic_scan(sweep_distance=.025, step_size=.005)
        print("Max Data Reading: {}".format(self.oscope.measure()))
        print("Max Data Location: ({}, {})".format(self.motion.get_motor_position(self.motion.x_mot), self.motion.get_motor_position(self.motion.y_mot)))
        self.basic_scan(sweep_distance=.01, step_size=.002)
        print("Max Data Reading: {}".format(self.oscope.measure()))
        print("Max Data Location: ({}, {})".format(self.motion.get_motor_position(self.motion.x_mot), self.motion.get_motor_position(self.motion.y_mot)))
        self.basic_scan(sweep_distance=.001, step_size=.0005)
        print("Max Data Reading: {}".format(self.oscope.measure()))
        print("Max Data Location: ({}, {})".format(self.motion.get_motor_position(self.motion.x_mot), self.motion.get_motor_position(self.motion.y_mot)))

    def auto_scan_small(self):
        """
        Performs basic scans of varying sizes to find location where highest readings are returned on a small scale.
        """
        self.basic_scan(sweep_distance=.01, step_size=.002)
        self.basic_scan(sweep_distance=.001, step_size=.0005)

    def basic_scan(self, sweep_distance, step_size, plot=False, sleep_time=.2):
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
        """
        max_data = 0
        max_data_loc = 0

        x_start_place = self.motion.get_motor_position(self.motion.x_mot) - (sweep_distance/2.0)
        y_start_place = self.motion.get_motor_position(self.motion.y_mot) - (sweep_distance/2.0)
        self.motion.go_to_stage_coordinates(x_start_place, y_start_place)
        time.sleep(sleep_time)

        self.motion.set_jog_step_linear(step_size)

        edge_Num = round(sweep_distance / step_size)
        data = np.zeros((edge_Num, edge_Num))
        rows, cols = data.shape

        if plot:
            fig, ax = plt.subplots(1,1)
            im = ax.imshow(data, cmap='hot') 

        moving_down = False

        for i in range(rows):
            for j in range(cols):
                data[i, j] = self.oscope.measure()
                print(data[i, j])
                if data[i, j] > max_data:
                    max_data = data[i, j]
                    max_data_loc = [self.motion.get_motor_position(self.motion.x_mot), self.motion.get_motor_position(self.motion.y_mot)]

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
            self.motion.move_step(self.motion.x_mot, "forward")
            time.sleep(sleep_time)

        self.motion.go_to_stage_coordinates(max_data_loc[0], max_data_loc[1])
        time.sleep(sleep_time)
        if plot:
            plt.show()