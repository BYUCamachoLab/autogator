import ctypes as ct
import warnings
import time
import threading

import numpy as np
from autogator.MotionControl import CINT, list1

# Import piezo controller DLL
dll = ct.CDLL("Thorlabs.MotionControl.Benchtop.Piezo.dll")

class Piezo(object):

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
        result = dll.PBC_Open(self._serial_number)
        if result != 0:
            raise RuntimeError("Error connecting (code: " + str(result) + ")")
        self._pause_for_device()

        # Get the channel count
        self._channels = dll.PBC_GetNumChannels(self._serial_number)

        # TODO: Reconsider this parameter
        # Get the minimum step size each channel allows.
        self._min_step_size = 0.005

        # Get the max distance of the actuator by channel (units: 100nm).
        travels = []
        for channel in range(1, self._channels + 1):
            travels.append(dll.PBC_GetMaximumTravel(self._serial_number, channel))
        self._max_travel = list1(travels)

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
        return int(self._serial_number.value.decode())

    def open_loop(self, channel):
        """
        Set a specified channel to "Open Loop" mode.

        Parameters
        ----------
        channel : int
            The channel to calculate to open loop mode (1 to n).

        # TODO: Update terminology to match ThorLabs documentation.
        CONTROL_MODE = 1 : Open Loop Mode
        CONTROL_MODE = 2 : Closed Loop Mode
        """
        # TODO: Does the second argument need to be a c_short?
        dll.PBC_SetPositionControlMode(self._serial_number, ct.c_short(channel), ct.c_short(1))
        # self._pause_for_device()

    def closed_loop(self, channel):
        """
        Set a specified channel to "Closed Loop" mode.

        Parameters
        ----------
        channel : int
            The channel to calculate to closed loop mode (1 to n).

        # TODO: Update terminology to match ThorLabs documentation.
        CONTROL_MODE = 1 : Open Loop Mode
        CONTROL_MODE = 2 : Closed Loop Mode
        """
        # TODO: Does the second argument need to be a c_short?
        dll.PBC_SetPositionControlMode(self._serial_number, ct.c_short(channel), ct.c_short(2))
        # self._pause_for_device()

    def identify(self, channel):
        """
        Sends a command to the device/channel to identify itself.

        Parameters
        ----------
        channel : int
            The channel to identify (1 to n).
        """
        dll.PBC_Identify(self._serial_number, ct.c_short(channel))

    def zero(self, channel):
        """
        Zeros a channel.

        Parameters
        ----------
        channel : int
            The channel to zero (1 to n).
        """
        x = threading.Thread(target=self._zero, args=(channel,), daemon=True)
        x.start()

    def _zero(self, channel):
        dll.PBC_SetZero(self._serial_number, ct.c_short(channel))
        time.sleep(25)
        self.move_to(channel, 1.0)

    def move_to(self, channel, position):
        """
        Set the position of the given channel to the specified position in micrometers.

        Parameters
        ----------
        channel : int
            The channel to move (1 to n).
        position : float
            Absolute position to move to, in micrometers.
        """
        # TODO: Do we want printed user warnings or to raise RuntimeWarning?
        if position < 0:
            warnings.warn("Channel {} moved to {}, a negative position! Setting to 0.".format(channel, position), Warning)
            position = 0
        elif position > self._max_travel[channel]:
            warnings.warn("Channel {} moved to {}, which is out-of-bounds! Setting to max.".format(channel, position), Warning)
            position = self._max_travel[channel]

        pos = self._position2short(channel, position)
        if pos > CINT.SHRT_MAX.value:
            pos = CINT.SHRT_MAX.value
        dll.PBC_SetPosition(self._serial_number, ct.c_short(channel), ct.c_short(pos))

    def move_by(self, channel, step):
        """
        Increases the position of the given channel by a specified step distance.

        Parameters
        ----------
        step : float
            The distance (in micrometers) to change the position by (can be negative).
        channel : int
            The channel to step (1 to n).
        """
        if np.abs(step) < self._min_step_size: 
            step = np.sign(step) * self._min_step_size
        self.move_to(channel, self.position(channel) + step)

    def position(self, channel):
        """
        Calculates the current position of some channel, in micrometers.

        The position returned by PBC_GetPosition is a percentage of maximum travel;
        its range is -32767 and 32767 corresponding to -100% and 100% respectively.

        Parameters
        ----------
        channel : int
            The channel to calculate the position for (1 to n).

        Returns
        -------
        pos : float
            The position of the requested channel, in micrometers.

        Raises
        ------
        RuntimeError
            If a request to get the actual position fails.
        """
        error = dll.PBC_RequestActualPosition(self._serial_number, ct.c_short(channel))
        if error != 0:
            raise RuntimeError("Failed to request position (error code ", error, ").")
        self._pause_for_device()
        position = dll.PBC_GetPosition(self._serial_number, ct.c_short(channel))

        # Convert max_travel from 100nm to um
        max_travel = self._max_travel[channel] / 10
        return max_travel * (float(position) / float(CINT.SHRT_MAX.value))

    def _position2short(self, channel, position):
        """
        Calculates the needed input as a percentage of max travel as a short from 0 to 32767.

        Parameters
        ----------
        channel : int
            The channel to calculate the position for (1 to n).
        position : float
            The position in micrometers.

        Returns
        -------
        out : int
            An integer between 0 to 32767, representing a percentage of the max travel 
            (corresponds to 0% to 100%, respectively).
        """
        # Convert position from um to 100nm
        position_100nm = 10 * position
        return int(CINT.SHRT_MAX.value * (position_100nm / float(self._max_travel[channel])))