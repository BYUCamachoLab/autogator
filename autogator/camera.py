# The documentation for Instrumental-lib by Mabuchi Lab can be located at 
# http://instrumental-lib.readthedocs.io/en/stable/index.html

import time
from enum import IntEnum

import cv2
import numpy as np
from instrumental import instrument
from instrumental.drivers.cameras import uc480
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation

plt.rcParams['toolbar'] = 'None'

class Camera(object):
    def __init__(self):
        pass

def grab_frame():
    # return np.random.normal(size=(100,150))
    return camera.snapshot()

def on_click(event):
    if event.button == MouseBtn.RIGHT_BTN:
        print("Setting point at:", event.xdata, event.ydata)
    if event.dblclick:
        if event.inaxes is not None:
            print(event.xdata, event.ydata)
            camera.h0 += int(event.xdata - 150/2)
            camera.v0 += int(event.ydata - 100/2)
        else:
            print("Not a valid location.")

#create subplots
fig, ax1 = plt.subplots()
ax1.axes.get_xaxis().set_visible(False)
ax1.axes.get_yaxis().set_visible(False)

fig.canvas.set_window_title('Live Camera')
fig.canvas.callbacks.connect('button_press_event', on_click)

#create image plots
im1 = ax1.imshow(grab_frame())

def update(i):
    im1.set_data(grab_frame())

ani = FuncAnimation(plt.gcf(), update, interval=20)
plt.tight_layout()
plt.show()









def detect():
    paramsets = uc480.list_instruments()
    i = 1
    print("Detected devices")
    for item in paramsets:
        print(i, ')', item)
        i += 1

def livestream():
    paramsets = uc480.list_instruments()
    # Assuming only one camera device is connected, the camera we want to connect
    # to will be the only one in the instrument list.

    camera = instrument(paramsets[0])

    #initialize live camera feed
    camera.start_live_video()
    #this loop updates the image being shown
    while camera.wait_for_frame():
        frame = camera.latest_frame()
        cv2.imshow('frame',frame)
        #wait 100 ms
        cv2.waitKey(100)
        #checks to see if the window was closed if closed exit loop to stop image from refreshing
        #without this the loop will automatically open a new window
        if cv2.getWindowProperty('frame',cv2.WND_PROP_VISIBLE) < 1: 
            break
    #I down loaded the source files for instrumental from git hum they are at C:\Users\ecestudent\Downloads\Instrumental-master
    cv2.destroyAllWindows()

if __name__ == '__main__':
    livestream()
