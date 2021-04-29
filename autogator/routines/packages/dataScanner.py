import os
os.environ['PATH'] = "C:\\Program Files\\ThorLabs\\Kinesis" + ";" + os.environ['PATH']

import pyvisa as visa
from packages.motion import *
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import atexit

from pyrolab.drivers.motion.z825b import Z825B

class DataScanner:
    def __init__(self, oscilloscope, channel=1):
        self.oscope = oscilloscope
        self.oscope.set_timescale(1e-9)
        self.oscope.set_channel(channel, range=.4, coupling="DCLimit", position=0)
        self.oscope.set_auto_measurement(1)
        self.oscope.wait_for_device()

    def get_data(self):
        return self.oscope.measure()

    def auto_scan(self):   
        self.basic_scan(sweep_distance=.025, step_size=.005)
        print("Max Data Reading: {}".format(self.oscope.measure()))
        print("Max Data Location: ({}, {})".format(get_x_position(), get_y_position()))
        self.basic_scan(sweep_distance=.01, step_size=.001)
        print("Max Data Reading: {}".format(self.oscope.measure()))
        print("Max Data Location: ({}, {})".format(get_x_position(), get_y_position()))
        self.basic_scan(sweep_distance=.001, step_size=.0005)
        print("Max Data Reading: {}".format(self.oscope.measure()))
        print("Max Data Location: ({}, {})".format(get_x_position(), get_y_position()))

    def basic_scan(self, sweep_distance, step_size):
        max_data = 0
        max_data_loc = 0

        x_start_place = get_x_position() + sweep_distance/2
        y_start_place = get_y_position() + sweep_distance/2
        go_to_chip_coordinates(x_start_place, y_start_place)

        set_jog_step_linear(step_size)

        edge_Num = round(sweep_distance / step_size)
        data = np.zeros((edge_Num, edge_Num))
        rows, cols = data.shape

        moving_down = True

        for i in range(rows):
            for j in range(cols):
                data[i, j] = self.oscope.measure()

                if data[i, j] > max_data:
                    max_data = data[i, j]
                    max_data_loc = [get_x_position(), get_y_position()]

                if moving_down:
                    move_down()
                else:
                    move_up()

            if moving_down:
                moving_down = False
            else:
                moving_down = True
        
            move_left()

        go_to_chip_coordinates(max_data_loc[0], max_data_loc[1])


    def basic_Scan_plot(self, sweep_distance = .05, step_size = 0.005):
        max_data = 0
        max_data_loc = 0

        print("Going to starting location...")
        x_start_place = get_x_position() + sweep_distance/2
        y_start_place = get_y_position() + sweep_distance/2
        go_to_chip_coordinates(x_start_place, y_start_place)

        SHAPE = round(sweep_distance / step_size)
        data = np.zeros((SHAPE, SHAPE))
        print("Scan grid: {}x{}".format(*data.shape))

        fig, ax = plt.subplots(1,1)
        im = ax.imshow(data, cmap='hot')  

        set_jog_step_linear(step_size)

        rows, cols = data.shape

        edge_y_position = get_y_position()

        for i in range(rows):
            for j in range(cols):
                data[i, j] = self.oscope.measure()

                if data[i, j] > max_data:
                    max_data = data[i, j]
                    max_data_loc = [get_x_position(), get_y_position()]

                move_down()

                im.set_data(data)
                im.set_clim(data.min(), data.max())
                fig.canvas.draw_idle()
                plt.pause(0.000001)
        
            move_left()
            
            go_to_chip_coordinates_y(edge_y_position)

        go_to_chip_coordinates(max_data_loc[0], max_data_loc[1])
        print("Done basic Scan")
        print("Max Data Reading: {}".format(max_data))
        print("Max Data Location: ({}, {})".format(max_data_loc[0], max_data_loc[1]))

        plt.show()


    