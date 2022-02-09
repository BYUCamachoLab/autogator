# -*- coding: utf-8 -*-
#
# Copyright © Autogator Project Contributors
# Licensed under the terms of the GNU GPLv3+ License
# (see autogator/__init__.py for details)

"""
Hardware
========

AutoGator has a number of optional hardware components that can be used to
control the motion of the PIC chip and other aspects of the system.
"""

import importlib
import logging
from pathlib import Path
from tkinter import N
from typing import Any, Dict, List, Tuple, Type

import numpy as np
from pydantic import BaseModel, BaseSettings

from autogator.errors import UncalibratedStageError
try:
    from pyrolab.api import locate_ns, Proxy
    from pyrolab.drivers.scopes.rohdeschwarz import RTO
except:
    pass

from autogator.circuit import CircuitMap


log = logging.getLogger(__name__)


class HardwareDevice:
    driver = None


class LinearStageBase(HardwareDevice):
    """
    A linear motor.

    This class is used to control a linear motor.

    Parameters
    ----------
    name : str
        The name of the motor.
    axis : Tuple[float, float, float]
        The axis of the motor as a 3-vector.
    """
    def __init__(self, name, axis=Tuple[float, float, float]):
        self.name = name
        self.axis = axis

    def move_to(self, position):
        """
        Move the motor to a position.

        Parameters
        ----------
        position : float
            The position to move the motor to.
        """
        log.info(f"Moving {self.name} to {position}")

    def move_by(self, distance: float):
        """
        Move the motor by a distance.

        Some motors have the capability for more accurate "jogs." This function
        exists to support that capability. Motors that don't have this
        capability can mock its effectse by simply using :py:func:`move_to`.

        Parameters
        ----------
        distance : float
            The distance to move the motor. A positive value will move the
            motor forward, and a negative value will move the motor backwards.
        """
        log.info(f"Moving {self.name} by {distance}")

    def move_cont(self, direction: float):
        """
        Move the motor continuously in the specified direction.

        A positive value for direction will move the motor in its forward 
        sense. A negative value will move the motor in its reverse sense.
        The magnitude of direction correlates with the speed of the move.

        Parameters
        ----------
        direction : float
            The direction and velocity with which to start moving the motor.
        """
        log.info(f"Moving {self.name} continuously in {direction}")

    def stop(self):
        """
        Stops all current motion.
        """
        log.info(f"Stopping {self.name}")

    def get_position(self) -> float:
        """
        Get the current position of the motor.

        Returns
        -------
        float
            The current position of the motor.
        """
        log.info(f"Getting position of {self.name}")
        return 0.0

    def home(self):
        """
        Move the motor to its home position.
        """
        log.info(f"Homing {self.name}")

    def status(self) -> int:
        """
        Whether the motor is doing something. Codes are device dependent.

        A status of 0 should always mean that the motor is idle and waiting
        for a command.

        Returns
        -------
        int
            The current status of the motor.
        """
        log.info(f"Getting status of {self.name}")
        return 0


class RotationalStageBase(HardwareDevice):
    """
    A rotational motor.

    This class is used to control a rotational motor.

    Parameters
    ----------
    name : str
        The name of the motor.
    axis : Tuple[float, float, float]
        The axis of the motor as a 3-vector.
    """
    def __init__(self, name, axis=Tuple[float, float, float]):
        self.name = name
        self.axis = axis

    def move_to(self, position):
        """
        Move the motor to a position.

        Parameters
        ----------
        position : float
            The position to move the motor to.
        """
        log.info(f"Moving {self.name} to {position}")

    def move_by(self, distance):
        """
        Move the motor by a distance.

        Some motors have the capability for more accurate "jogs." This function
        exists to support that capability. Motors that don't have this
        capability can mock its effectse by simply using :py:func:`move_to`.

        Parameters
        ----------
        distance : float
            The distance to move the motor.
        """
        log.info(f"Moving {self.name} by {distance}")

    def move_cont(self, direction: float):
        """
        Move the motor continuously in the specified direction.

        A positive value for direction will move the motor in its forward 
        sense. A negative value will move the motor in its reverse sense.
        The magnitude of direction correlates with the speed of the move.

        Parameters
        ----------
        direction : float
            The direction and velocity with which to start moving the motor.
        """
        log.info(f"Moving {self.name} continuously in {direction}")

    def stop(self):
        """
        Stops all current motion.
        """
        log.info(f"Stopping {self.name}")

    def get_position(self) -> float:
        """
        Get the current position of the motor.

        Returns
        -------
        float
            The current position of the motor.
        """
        log.info(f"Getting position of {self.name}")
        return 0.0

    def home(self):
        """
        Move the motor to its home position.
        """
        log.info(f"Homing {self.name}")

    def status(self) -> int:
        """
        Whether the motor is doing something. Codes are device dependent.

        A status of 0 should always mean that the motor is idle and waiting
        for a command.

        Returns
        -------
        int
            The current status of the motor.
        """
        log.info(f"Getting status of {self.name}")
        return 0


class DataAcquisitionUnitBase(HardwareDevice):
    """
    A data acquisition unit.

    This class is used to control a data acquisition unit.

    Parameters
    ----------
    name : str
        The name of the data acquisition unit.
    """
    def __init__(self, name):
        self.name = name

    def measure(self):
        """
        Takes a single-shot measurement.

        Returns
        -------
        Any
            The measured data.
        """
        log.info(f"Measuring {self.name}")

    def acquire(self):
        """
        Asynchronous command to begin acquiring data.

        This method should acquire data from the data acquisition unit.
        """
        log.info(f"Acquiring data from {self.name}")

    def get_data(self):
        """
        Gets the acquired data.

        Returns
        -------
        Any
            The acquired data.
        """
        log.info(f"Getting data from {self.name}")


class LaserBase(HardwareDevice):
    """
    A laser.

    This class is used to control a laser.

    Parameters
    ----------
    name : str
        The name of the laser.
    """
    def __init__(self, name):
        self.name = name

    def on(self):
        """
        Turn the laser on.
        """
        log.info(f"Turning {self.name} on")

    def off(self):
        """
        Turn the laser off.
        """
        log.info(f"Turning {self.name} off")

    def power(self, power):
        """
        Set the power of the laser.

        Parameters
        ----------
        power : float
            The power of the laser.
        """
        log.info(f"Setting power of {self.name} to {power}")

    def wavelength(self, wavelength):
        """
        Set the wavelength of the laser.

        Parameters
        ----------
        wavelength : float
            The wavelength of the laser.
        """
        log.info(f"Setting wavelength of {self.name} to {wavelength}")

    def sweep(self):
        """
        Sweep the laser.
        """
        log.info(f"Sweeping {self.name}")


class CameraBase(HardwareDevice):
    """
    A camera.

    This class is used to control a camera.

    Parameters
    ----------
    name : str
        The name of the camera.
    """
    def __init__(self, name):
        self.name = name

    def get_frame(self):
        """
        Take a picture.

        This method should take a picture from the camera.
        """
        log.info(f"Taking picture from {self.name}")


class Stage:
    """
    Singleton that centralizes access to all hardware devices. 

    If you know a certain stage axis supports more complex functions, you can
    access the object directly using the ``driver`` attribute, e.g.:
    
    .. code-block:: python

        x_motor = stage.x.driver
        x_motor.unexposed_function()

    Additionally, any "auxiliary" devices can also be directly accessed as 
    attributes, e.g.:

    .. code-block:: python

        daq = stage.daq
        daq.measure()
        daq.driver.unexposed_function()

    Parameters
    ----------
    """    
    def __init__(
        self, 
        x: LinearStageBase, 
        y: LinearStageBase, 
        z: LinearStageBase, 
        theta: RotationalStageBase, 
        phi: RotationalStageBase, 
        psi: RotationalStageBase, 
        circuitmap: CircuitMap, 
        conversion_matrix: np.ndarray = None, 
        loaded_position: List[float] = [None, None, None, None, None, None],
        unloaded_position: List[float] = [None, None, None, None, None, None],
        auxiliaries: Dict[str, HardwareDevice] = {},
    ):
        self.x = x
        self.y = y
        self.z = z
        self.theta = theta
        self.phi = phi
        self.psi = psi

        self.circuitmap = circuitmap
        self.conversion_matrix = conversion_matrix
        self.loaded_position = loaded_position
        self.unloaded_position = unloaded_position
        self.auxiliaries = auxiliaries

        # TODO: Implement?
        # self._last_calibrated = None
        # self._last_homed = None

    def __getattr__(self, name):
        if name in self.auxiliaries:
            return self.auxiliaries[name]
        else:
            raise AttributeError(f"'Stage' object has no attribute '{name}'")

    @property
    def motors(self) -> list:
        """
        Returns a list of all motors.
        """
        return [self.x, self.y, self.z, self.theta, self.phi, self.psi]

    def set_position(self, x=None, y=None, z=None, theta=None, phi=None, psi=None):
        """
        Set the position of the stage in real world units.

        Any unspecified parameters won't be moved.

        Parameters
        ----------
        x : float, optional
            The x position.
        y : float, optional
            The y position.
        z : float, optional
            The z position.
        theta : float, optional
            The theta position.
        phi : float, optional
            The phi position.
        psi : float, optional
            The psi position.
        """
        pos = [x, y, z, theta, phi, psi]
        commands = [cmd for cmd in zip(self.motors, pos) if cmd[1] is not None]
        for motor, pos in commands:
            if motor:
                motor.move_to(pos)

    def set_position_gds(self, x=None, y=None):
        """
        Set the position of the stage in GDS coordinates.

        Only supports 2D commands, i.e. (x, y) coordinates. Any unspecified 
        parameters won't be moved.

        Parameters
        ----------
        x : float, optional
            The x position.
        y : float, optional
            The y position.

        Raises
        ------
        UncalibratedStageError
            If the stage is not calibrated. GDS position cannot be set without
            first calibrating the stage.
        """
        if not self.conversion_matrix:
            raise UncalibratedStageError("Stage is not calibrated (no conversion matrix set), cannot set position in GDS coordinates")

        x_cmd = x if x is not None else 0.0
        y_cmd = y if y is not None else 0.0
        gds_pos = np.array([[x_cmd], [y_cmd], [1]])
        stage_pos = self.conversion_matrix @ gds_pos

        if x and self.x:
            self.x.move_to(stage_pos[0][0])
        if y and self.y:
            self.y.move_to(stage_pos[1][0])

    def get_position(self) -> List[float]:
        """
        Returns the current position of the stage.

        Returns
        -------
        list
            A list of the current position of each motor.
        """
        return [motor.get_position() if motor else None for motor in self.motors]

    def stop_all(self) -> None:
        """
        Stops motor motion is it is moving conintuously and marks motor as not moving.

        This function should not block! In the case of multiple motors, 
        be careful that calling stop on each may wait until completion before
        returning! In the case of an emergency stop, you want all motors to 
        stop essentially instantaneously. Perhaps spawn them all in a thread?
        """
        for motor in self.motors:
            if motor:
                motor.stop()
                # if motor.status() != 0:
                #     motor.stop()

    def load(self):
        """
        Load the stage.

        This method should load the stage.
        """
        log.info("Loading stage")
        self.set_position(*self.loaded_position)

    def unload(self):
        """
        Unload the stage.

        This method should unload the stage.
        """
        log.info("Unloading stage")
        self.set_position(*self.unloaded_position)


class HardwareConfiguration(BaseSettings):
    module: str = "autogator.hardware"
    classname: str
    parameters: Dict[str, Any] = {}

    def get_object(self) -> Type[HardwareDevice]:
        log.debug(f"Attempting to load '{self.module}.{self.classname}'")
        try:
            mod = importlib.import_module(self.module)
            log.debug("Module found...")
            obj: HardwareDevice = getattr(mod, self.classname)
            log.debug("Class found...")
        except Exception as e:
            log.critical(e)
            raise e
        
        obj = obj(**self.parameters)
        log.debug("Object instantiated...")

        return obj


class StageConfiguration(BaseSettings):
    """
    The persisted stage configuration.

    Attributes
    ----------
    x : HardwareConfiguration
        The configuration for the x-axis stage.
    y : HardwareConfiguration
        The configuration for the y-axis stage.
    z : HardwareConfiguration
        The configuration for the z-axis stage.
    theta : HardwareConfiguration
        The configuration for the rotational stage in the x-z plane.
    phi : HardwareConfiguration
        The configuration for the rotational stage in the y-z plane.
    psi : HardwareConfiguration
        The configuration for the rotational stage in the x-y plane.
    circuitmap : str
        Path to the CircuitMap text file.
    conversion_matrix : str
        Path to the conversion matrix text file.
    loaded_position : List[float]
        List (length 6) of motor positions when the stage is loaded.
    unloaded_position : List[float]
        List (length 6) of motor positions when the stage is unloaded.
    auxiliaries : Dict[str, HardwareConfiguration]
        A dictionary of auxiliary hardware devices.
    """
    x: HardwareConfiguration = None
    y: HardwareConfiguration = None
    z: HardwareConfiguration = None
    theta: HardwareConfiguration = None
    phi: HardwareConfiguration = None
    psi: HardwareConfiguration = None
    circuitmap: str = ""
    conversion_matrix: str = ""
    loaded_position: List[Any] = [None, None, None, None, None, None]
    unloaded_position: List[Any] = [None, None, None, None, None, None]
    auxiliaries: Dict[str, HardwareConfiguration] = {}

    def get_stage(self) -> Stage:
        """
        Returns
        -------
        Stage
            The stage object.
        """
        cmapfile = Path(self.circuitmap)
        circuitmap = CircuitMap.loadtxt(cmapfile) if cmapfile.is_file() else None

        cmatfile = Path(self.conversion_matrix)
        conversion_matrix = CircuitMap.loadtxt(cmatfile) if cmatfile.is_file() else None

        log.info("Loading stage objects...")
        auxiliaries = {}

        try:
            log.info("Loading x-axis stage...")
            x = self.x.get_object() if self.x else None
        except Exception as e:
            log.exception(e)

        try:
            log.info("Loading y-axis stage...")
            y = self.y.get_object() if self.y else None
        except Exception as e:
            log.exception(e)

        try:
            log.info("Loading z-axis stage...")
            z = self.z.get_object() if self.z else None
        except Exception as e:
            log.exception(e)

        try:
            log.info("Loading theta stage...")
            theta = self.theta.get_object() if self.theta else None
        except Exception as e:
            log.exception(e)

        try:
            log.info("Loading phi stage...")
            phi = self.phi.get_object() if self.phi else None
        except Exception as e:
            log.exception(e)

        try:
            log.info("Loading psi stage...")
            psi = self.psi.get_object() if self.psi else None
        except Exception as e:
            log.exception(e)

        for name, config in self.auxiliaries.items():
            try:
                log.info(f"Loading auxiliary hardware '{name}'...")
                auxiliaries[name] = config.get_object()
            except Exception as e:
                log.exception(e)

        log.info("Stage objects loaded.")
        return Stage(x, y, z, theta, phi, psi, circuitmap, conversion_matrix,
                     self.loaded_position, self.unloaded_position,
                     auxiliaries)


###############################################################################


class Z825BLinearStage(LinearStageBase):
    """
    A linear motor.
    """
    def __init__(self, pyroname: str = "", ns_host: str = "localhost", ns_port: int = 9090):
        super().__init__(pyroname)
        with locate_ns(host=ns_host, port=ns_port) as ns:
            self.driver = Proxy(ns.lookup(pyroname))
            self.driver.autoconnect()
        self._step_size = None

    def __del__(self):
        self.driver._pyroClaimOwnership()
        self.driver.close()

    @property
    def step_size(self):
        """The jog step size in mm."""
        return self._step_size

    @step_size.setter
    def step_size(self, step_size: float):
        if step_size != self._step_size:
            self.driver._pyroClaimOwnership()
            self.driver.jog_step_size = step_size
            self._step_size = step_size

    def move_to(self, position: float):
        """
        Moves to a new position.

        This motor adjusts for backlash; a given position will always be 
        approached from the "negative" direction. That may require overshooting 
        the commanded position in order to approach it again from a consistent
        direction.

        If stepping in short steps, it is therefore most efficient to step
        from negative to positive values to avoid backlash adjustments on 
        each step.

        Parameters
        ----------
        position : float
            The new position to move to.
        """
        self.driver._pyroClaimOwnership()
        if self._requires_backlash_adjustment(position):
            self.driver.move_to(position - (self.driver.backlash * 1.5))
        self.driver.move_to(position)

    def move_by(self, distance: float):
        """
        Jogs the motor by a fixed distance.

        Parameters
        ----------
        distance : float
            The distance to move the motor. A positive value will move the
            motor forward, and a negative value will move the motor backwards.
        """
        self.driver._pyroClaimOwnership()
        if np.abs(distance) != self.step_size:
            self.step_size = np.abs(distance)
        if distance > 0:
            self.driver.jog("forward")
        else:
            self.driver.jog("backward")

    def move_cont(self, direction: str) -> None:
        """
        Starts a continuous move in the specified direction.

        Parameters
        ----------
        direction : str
            The direction to move the motor, either "forward" or "backward".
        """
        self.driver._pyroClaimOwnership()
        self.driver.move_continuous(direction)

    def _requires_backlash_adjustment(self, position: float) -> bool:
        """
        Determine if the new position command needs to compensate for backlash.

        The ThorLabs linear stages have a small backlash distance. To ensure
        as accurate a reposition as possible when moving to the same location
        multiple times, the motor will always approach the position from the 
        same direction. This function determines whether that requires 
        overshooting the current position before reapproaching.

        Parameters
        ----------
        position : float
            The position to move to.

        Returns
        -------
        bool
            Whether backlash compensation is required.
        """
        if position < self.get_position():
            return True
        return False

    def stop(self):
        """
        Stop all motion.
        """
        self.driver._pyroClaimOwnership()
        self.driver.stop()

    def get_position(self) -> float:
        """
        Get the current position in millimeters.
        """
        self.driver._pyroClaimOwnership()
        return self.driver.get_position()

    def home(self):
        """
        Home the motor.
        """
        self.driver._pyroClaimOwnership()
        self.driver.go_home()

    def status(self):
        """
        Returns a nonzero value if the motor is busy.
        """
        pass


class PRM1Z8RotationalStage(RotationalStageBase):
    """
    A rotational motor.
    """
    def __init__(self, pyroname: str = "", ns_host: str = "localhost", ns_port: int = 9090):
        super().__init__(pyroname)
        with locate_ns(host=ns_host, port=ns_port) as ns:
            self.driver = Proxy(ns.lookup(pyroname))
            self.driver.autoconnect()
        self._step_size = None

    def __del__(self):
        self.driver._pyroClaimOwnership()
        self.driver.close()

    @property
    def step_size(self):
        """The jog step size in mm."""
        return self._step_size

    @step_size.setter
    def step_size(self, step_size: float):
        if step_size != self._step_size:
            self.driver._pyroClaimOwnership()
            self.driver.jog_step_size = step_size
            self._step_size = step_size

    def move_to(self, position: float):
        """
        Moves to a new position.

        This motor adjusts for backlash; a given position will always be 
        approached from the same direction. That may require overshooting the
        commanded position in order to approach it again from a consistent
        direction.

        Parameters
        ----------
        position : float
            The new position to move to.
        """
        self.driver._pyroClaimOwnership()
        if self._requires_backlash_adjustment(position):
            self.driver.move_to(position - (self.driver.backlash * 1.5))
        self.driver.move_to(position)

    def move_by(self, distance: float):
        """
        Jogs the motor by a fixed distance.

        Parameters
        ----------
        distance : float, optional
            The distance to move the motor. A positive value will move the
            motor forward, and a negative value will move the motor backwards.
        """
        self.driver._pyroClaimOwnership()
        if np.abs(distance) != self.step_size:
            self.step_size = np.abs(distance)
        if distance > 0:
            self.driver.jog("forward")
        else:
            self.driver.jog("backward")

    def move_cont(self, direction: str) -> None:
        """
        Starts a continuous move in the specified direction.

        Parameters
        ----------
        direction : str
            The direction to move the motor, either "forward" or "backward".
        """
        self.driver._pyroClaimOwnership()
        self.driver.move_continuous(direction)

    def _requires_backlash_adjustment(self, position: float) -> bool:
        """
        Determine if the new position command needs to compensate for backlash.

        The ThorLabs linear stages have a small backlash distance. To ensure
        as accurate a reposition as possible when moving to the same location
        multiple times, the motor will always approach the position from the 
        same direction. This function determines whether that requires 
        overshooting the current position before reapproaching.

        Parameters
        ----------
        position : float
            The position to move to.

        Returns
        -------
        bool
            Whether backlash compensation is required.
        """
        if position < self.get_position():
            return True
        return False

    def stop(self):
        """
        Stop all motion.
        """
        self.driver._pyroClaimOwnership()
        self.driver.stop()

    def get_position(self) -> float:
        """
        Get the current position in millimeters.
        """
        self.driver._pyroClaimOwnership()
        return self.driver.get_position()

    def home(self):
        """
        Home the motor.
        """
        self.driver._pyroClaimOwnership()
        self.driver.go_home()

    def status(self):
        """
        Returns a nonzero value if the motor is busy.
        """
        pass


class TSL550Laser(LaserBase):
    """
    A laser.
    """
    def __init__(self, pyroname: str = "", ns_host: str = "localhost", ns_port: int = 9090):
        super().__init__(pyroname)
        with locate_ns(host=ns_host, port=ns_port) as ns:
            self.driver = Proxy(ns.lookup(pyroname))
            self.driver.autoconnect()

    def __del__(self):
        self.driver._pyroClaimOwnership()
        self.driver.close()

    def on(self):
        self.driver._pyroClaimOwnership()
        if self.driver.status()[0] == '-':
            self.driver.on()
        self.driver.open_shutter()

    def off(self, diode: bool = True):
        """
        Turns off laser output by closing the shutter and optionally turning off the diode.

        Parameters
        ----------
        diode : bool, optional
            Whether to turn off the diode. If False, the laser diode will be
            turned off. There is a warm-up period to turn the laser back on if
            the diode has been turned off. If True, the laser diode will be
            left on but the shutter will be closed.
        """
        self.driver._pyroClaimOwnership()
        self.driver.close_shutter()
        if not diode:
            self.driver.off()

    def power(self, power: float):
        self.driver._pyroClaimOwnership()
        self.driver.power_dBm(power)

    def wavelength(self, wavelength: float):
        self.driver._pyroClaimOwnership()
        self.driver.wavelength(wavelength)

    def sweep(self, num: int = 1):
        """
        Run the configured wavelength sweep.

        Parameters
        ----------
        num : int, optional
            The number of times to run the wavelength sweep (default 1).
        """
        self.driver._pyroClaimOwnership()
        self.driver.sweep_start(num)

    def sweep_wavelength(self, wl_start: float = 1500, wl_stop: float = 1630, duration: float = 2, number: int = 1):
        """
        Convenience function to run a continuous wavelength sweep.

        Parameters
        ----------
        wl_start : float, optional
            The starting wavelength (default 1500).
        wl_stop : float, optional
            The ending wavelength (default 1630).
        duration : float, optional
            The duration of the sweep (default 2).
        number : int, optional
            The number of times to run the sweep (default 1).
        """
        self.driver._pyroClaimOwnership()
        self.driver.sweep_wavelength(start=wl_start, stop=wl_stop, duration=duration, number=number)

    def sweep_set_mode(
        self, continuous: bool, twoway: bool, trigger: bool, const_freq_step: bool
    ):
        self.driver._pyroClaimOwnership()
        self.driver.sweep_set_mode(
            continuous=continuous,
            twoway=twoway,
            trigger=trigger,
            const_freq_step=const_freq_step,
        )

    def set_trigger(self, mode: str, step: float):
        self.driver._pyroClaimOwnership()
        self.driver.trigger_enable_output()
        triggerMode = self.driver.trigger_set_mode(mode)
        triggerStep = self.driver.trigger_set_step(step)
        return triggerMode, triggerStep

    def wavelength_logging(self):
        self.driver._pyroClaimOwnership()
        return self.driver.wavelength_logging()

    
class RohdeSchwarzOscilliscope(DataAcquisitionUnitBase):
    def __init__(self, name: str, address: str, hislip: bool = False, timeout: float = 1000.0):
        super().__init__(name)
        self.driver = RTO()
        self.driver.connect(address, hislip=hislip, timeout=timeout)

    def __del__(self):
        self.driver.close()

    def measure(self) -> float:
        """
        Performs a single-shot measurement.

        Returns
        -------
        float
            The measured value.
        """
        return self.driver.measure()

    def acquire(self, timeout: float = -1):
        """
        Asynchronous command that starts acquisition.
        """
        self.driver.acquire(timeout=timeout)

    def get_data(self, channel: int):
        return self.driver.get_data(channel)

    def wait_for_device(self):
        self.driver.wait_for_device()

    def set_channel(self, channel: int, range: float, coupling: str, position: float):
        self.driver.set_channel(channel, range=range, coupling=coupling, position=position)

    def set_channel_for_auto_measurement(
        self,
        channel: int,
        range: float,
        coupling: str,
        position: float,
        timescale: float,
    ):
        self.driver.set_timescale(timescale)
        self.set_channel(channel, range=range, coupling=coupling, position=position)
        self.driver.set_auto_measurement(source="C" + str(channel) + "W1")
        self.wait_for_device()

    def set_acquisition_settings(self, sample_rate: float, duration: float):
        self.driver.acquisition_settings(
            sample_rate=sample_rate, duration=duration
        )

    def set_edge_trigger(self, trigger_channel: int, trigger_level: int):
        self.driver.edge_trigger(trigger_channel, trigger_level)
