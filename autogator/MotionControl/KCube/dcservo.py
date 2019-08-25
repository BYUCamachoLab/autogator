import ctypes as ct
import time
# import threading

import numpy as np
from autogator.MotionControl import CINT, list1

# Import DCServo controller DLL
dll = ct.CDLL("Thorlabs.MotionControl.KCube.DCServo.dll")

class DCServo(object):

    def __init__(self, serial_number):
        """
        Initializes the connection to the piezo controller. 
        
        Raises
        ------
        RuntimeError
            Raises a runtime error if the connection is unsuccessful.
        """
        self._serial_number = ct.c_char_p(str(serial_number).encode())

        # Connect to the device
        result = dll.CC_Open(self._serial_number)
        if result != 0:
            raise RuntimeError("Error connecting (code: " + str(result) + ")")
        # self._pause_for_device()

        # Get the channel count
        # self._channels = dll.PBC_GetNumChannels(self._serial_number)

        # TODO: Reconsider this parameter
        # Get the minimum step size each channel allows.
        # self._min_step_size = 0.005

        # Get the max distance of the actuator by channel (units: 100nm).
        # travels = []
        # for channel in range(1, self._channels + 1):
        #     travels.append(dll.PBC_GetMaximumTravel(self._serial_number, channel))
        # self._max_travel = list1(travels)

    def _pause_for_device(self):
        """
        Sleep 50ms for device to respond.

        Several functions seem to provide the wrong information without a pause between
        the request and the actual acquisition of data. This function provides a 50ms
        pause for the controller to catch up.
        """
        time.sleep(0.05)

    def disconnect(self):
        """
        Disconnects and closes the KCube device.
        """
        dll.CC_Close(self._serial_number)

    @property
    def serial_number(self):
        """
        Returns the serial number of the controller.

        Returns
        -------
        serial : int
            The serial number of the controller.
        """
        return int(self._serial_number.value.decode())

    def identify(self):
        """
        Sends a command to the device to make it identify itself.
        """
        dll.CC_Identify(self._serial_number)

    def home(self):
        """
        Home the device.

        Parameters
        ----------
        channel : int
            The channel to zero (1 to n).
        """
        dll.CC_Home(self._serial_number)

    def move_to(self, position):
        """
        Set the position of the given channel to the specified position in micrometers.

        Parameters
        ----------
        position : float
            Absolute position to move to, in micrometers.
        """
        # # TODO: Do we want printed user warnings or to raise RuntimeWarning?
        # if position < 0:
        #     warnings.warn("Channel {} moved to {}, a negative position! Setting to 0.".format(channel, position), Warning)
        #     position = 0
        # elif position > self._max_travel[channel]:
        #     warnings.warn("Channel {} moved to {}, which is out-of-bounds! Setting to max.".format(channel, position), Warning)
        #     position = self._max_travel[channel]

        # pos = self._position2short(channel, position)
        # if pos > CINT.SHRT_MAX.value:
        #     pos = CINT.SHRT_MAX.value
        # dll.PBC_SetPosition(self._serial_number, ct.c_short(channel), ct.c_short(pos))
        pass

    def move_by(self, step):
        """
        Increases the position of the given channel by a specified step distance.

        Parameters
        ----------
        step : float
            The distance (in micrometers) to change the position by (can be negative).
        channel : int
            The channel to step (1 to n).
        """
        # if np.abs(step) < self._min_step_size: 
        #     step = np.sign(step) * self._min_step_size
        # self.move_to(channel, self.position(channel) + step)
        pass

    def jog(self, direction):
        pass

    @property
    def position(self):
        """
        Calculates the current position of some channel, in micrometers.

        # The position returned by PBC_GetPosition is a percentage of maximum travel;
        # its range is -32767 and 32767 corresponding to -100% and 100% respectively.

        Returns
        -------
        pos : float
            The position of the requested channel, in micrometers.

        Raises
        ------
        RuntimeError
            If a request to get the actual position fails.
        """
        error = dll.CC_RequestPosition(self._serial_number)
        if error != 0:
            raise RuntimeError("Failed to request position (error code ", error, ").")
        self._pause_for_device()
        position = dll.CC_GetPosition(self._serial_number)
        
        print(position)