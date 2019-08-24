# The documentation for Instrumental-lib by Mabuchi Lab can be located at 
# http://instrumental-lib.readthedocs.io/en/stable/index.html
# The library can be installed via pip or by cloning the github package, 
# see the above site.

# import matplotlib to be able to display the captured image.
from instrumental import instrument
from matplotlib import pyplot
from instrumental.drivers.cameras import uc480
import cv2
import time

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