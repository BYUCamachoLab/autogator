import os
import sys
import ctypes as ct
from enum import Enum
import warnings

import numpy as np
import autogator.configurations as config

# Add location of the DLLs to PATH so that the program can run on any machine
dll_location = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'dll')
os.environ['PATH'] = dll_location + os.pathsep + os.environ['PATH']

# Import piezo controller DLL
dll = ct.CDLL("Thorlabs.MotionControl.Benchtop.Piezo.dll")

class CINT(Enum):
    """
    An enumeration of basic c-style integer constants.
    """
    CHAR_MIN = -128
    CHAR_MAX = 127
    SHRT_MIN = -32768
    SHRT_MAX = 32767
    USHRT_MAX = 65535
    INT_MIN = -2147483648
    INT_MAX = 2147483647
    UINT_MAX = 4294967295 


class BPC303(object):
    def __init__(self, serial_number):
        # TODO: Store maximum travel on init, store minimum step on init
        self._serial_number = serial_number
        self._min_step_size = 0.005
        self._max_travel = 20

    def _connect(self):
        """
        Initializes the connection to the piezo controller. 
        
        Raises
        ------
        RuntimeError
            Raises a runtime error if the connection is unsuccessful.
        """
        result = dll.PBC_Open(self._serial_number)
        if result != 0:
            raise RuntimeError("Error connecting (code:" + str(result) + ")")

    def _disconnect(self):
        """
        Disconnects the control from the computer so it no longer takes commands.
        """
        dll.PBC_Disconnect(self._serial_number)
        dll.PBC_Close(self._serial_number)

    @property
    def serial_number(self):
        """
        Returns the serial number of the piezo controller.

        Returns
        -------
        serial : int
            The serial number of the piezo controller.
        """
        return self._serial_number

    def open_loop(self, channel):
        """
        Set a specified channel to "Open Loop" mode.

        Parameters
        ----------
        channel : int
            The channel to calculate to open loop mode (1-3).

        # TODO: Update terminology to match ThorLabs documentation.
        CONTROL_MODE = 1 : Open Loop Mode
        CONTROL_MODE = 2 : Closed Loop Mode
        """
        # TODO: Does the second argument need to be a c_short?
        dll.PBC_SetPositionControlMode(self._serial_number, ct.c_short(channel), ct.c_short(1))

    def closed_loop(self, channel):
        """
        Set a specified channel to "Closed Loop" mode.

        Parameters
        ----------
        channel : int
            The channel to calculate to closed loop mode (1-3).

        # TODO: Update terminology to match ThorLabs documentation.
        CONTROL_MODE = 1 : Open Loop Mode
        CONTROL_MODE = 2 : Closed Loop Mode
        """
        # TODO: Does the second argument need to be a c_short?
        dll.PBC_SetPositionControlMode(self._serial_number, ct.c_short(channel), ct.c_short(2))

    def identify(self, channel):
        """
        Sends a command to the device/channel to identify itself.

        Parameters
        ----------
        channel : int
            The channel to identify (1-3).
        """
        dll.PBC_Identify(self._serial_number, ct.c_short(channel))

    def zero(self, channel):
        """
        Zeros a channel.

        Parameters
        ----------
        channel : int
            The channel to zero (1-3).
        """
        dll.PBC_SetZero(self._serial_number, ct.c_short(channel))

    def move_to(self, channel, position):
        """
        Set the position of the given channel to the specified position in micrometers.

        Parameters
        ----------
        channel : int
            The channel to move (1-3).
        position : float
            Absolute position to move to, in micrometers.
        """
        # TODO: Do we want printed user warnings or to raise RuntimeWarning?
        if position < 0:
            warnings.warn("Channel {} moved to {}, a negative position! Setting to 0.".format(channel, position), Warning)
            position = 0
        elif position > self._max_travel:
            warnings.warn("Channel {} moved to {}, which is out-of-bounds! Setting to max.".format(channel, position), Warning)
            position = self._max_travel

        inputShort = self._calculateDistanceShort(position, channel)
        if inputShort > CINT.SHRT_MAX: 
            inputShort = CINT.SHRT_MAX
        inputShort = ct.c_short(inputShort)
        dll.PBC_SetPosition(self._serial_number, ct.c_short(channel), inputShort)

    def move_by(self, channel, step):
        """
        Increases the position of the given channel by a specified step distance.

        Parameters
        ----------
        step : float
            The distance (in micrometers) to change the position by (can be negative).
        channel : int
            The channel to step (1-3).
        """
        if np.abs(step) < self._min_step_size: 
            step = np.sign(step) * self._min_step_size
        self.move_to(channel, self.position(channel) + step)

    def position(self, channel):
        """
        Calculates the current position of some channel, in micrometers.

        Parameters
        ----------
        channel : int
            The channel to calculate the position for (1-3).

        Returns
        -------
        pos : float
            The position of the requested channel, in micrometers.
        """
        channel = ct.c_short(channel)
        error = dll.PBC_RequestActualPosition(self._serial_number, channel)
        positionShort = dll.PBC_GetPosition(self._serial_number, channel)

        # Convert the value returned from the channel (which is a percentage)
        # into its equivalent physical distance in micrometers (um).
        pyPosition = (ct.c_short(positionShort).value) # Is all this conversion necessary?
        max_travel = ct.c_short(dll.PBC_GetMaximumTravel(self._serial_number, channel)).value / 10
        percentOfMax = float(pyPosition) / float(CINT.SHRT_MAX)
        return percentOfMax * max_travel

    def _calculateDistanceShort(self, channel, position):
        """
        Calculates the needed input as a percentage of max travel as a short from 0 to 32767.

        Parameters
        ----------
        channel : int
            The channel to calculate the position for (1-3).
        position : float
            The position in micrometers.

        Returns
        -------
        out : int
            An integer between 0 to 32767, representing the percentage of max travel 
            (corresponds to 0% to 100%, respectively).
        """
        #set channel to channel currently in use
        channel = ct.c_short(channel)
        #gets the max distance of the actuator in 100nm
        maxTravel = ct.c_short(dll.PBC_GetMaximumTravel(self._serial_number, channel)).value
        #print maxTravel
        #convert position from um to 100nm
        position_100nm = 10 * position
        pecentageOfMax = position_100nm / float(maxTravel)
        inputShort = pecentageOfMax * CINT.SHRT_MAX
        return int(inputShort)