import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

class DataScanner:
    def __init__(self, oscilloscope, motion, channel=1):
        self.oscope = oscilloscope
        self.mot = motion
        self.oscope.set_timescale(1e-9)
        self.oscope.set_channel(channel, range=.4, coupling="DCLimit", position=0)
        self.oscope.set_auto_measurement(1)
        self.oscope.wait_for_device()

    def auto_scan(self):   
        self.basic_scan(sweep_distance=.025, step_size=.005)
        print("Max Data Reading: {}".format(self.oscope.measure()))
        print("Max Data Location: ({}, {})".format(self.mot.get_x_position(), self.mot.get_y_position()))
        self.basic_scan(sweep_distance=.01, step_size=.001)
        print("Max Data Reading: {}".format(self.oscope.measure()))
        print("Max Data Location: ({}, {})".format(self.mot.get_x_position(), self.mot.get_y_position()))
        self.basic_scan(sweep_distance=.001, step_size=.0005)
        print("Max Data Reading: {}".format(self.oscope.measure()))
        print("Max Data Location: ({}, {})".format(self.mot.get_x_position(), self.mot.get_y_position()))

    def basic_scan(self, sweep_distance, step_size, plot=False):
        max_data = 0
        max_data_loc = 0

        x_start_place = self.mot.get_x_position() + sweep_distance/2
        y_start_place = self.mot.get_y_position() + sweep_distance/2
        self.mot.go_to_chip_coordinates(x_start_place, y_start_place)

        self.mot.set_jog_step_linear(step_size)

        edge_Num = round(sweep_distance / step_size)
        data = np.zeros((edge_Num, edge_Num))
        rows, cols = data.shape

        if plot:
            fig, ax = plt.subplots(1,1)
            im = ax.imshow(data, cmap='hot') 

        moving_down = True

        for i in range(rows):
            for j in range(cols):
                data[i, j] = self.oscope.measure()

                if data[i, j] > max_data:
                    max_data = data[i, j]
                    max_data_loc = [self.mot.get_x_position(), self.mot.get_y_position()]

                if moving_down:
                    self.mot.move_step(self.y_mot, "backward")
                else:
                    self.mot.move_step(self.y_mot, "forward")

                if plot:
                    im.set_data(data)
                    im.set_clim(data.min(), data.max())
                    fig.canvas.draw_idle()
                    plt.pause(0.000001)

            if moving_down:
                moving_down = False
            else:
                moving_down = True
        
            self.mot.move_step(self.x_mot, "forward")

        self.mot.go_to_chip_coordinates(max_data_loc[0], max_data_loc[1])
        if plot:
            plt.show()