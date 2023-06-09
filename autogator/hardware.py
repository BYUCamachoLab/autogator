# -*- coding: utf-8 -*-
#
# Copyright © Autogator Project Contributors
# Licensed under the terms of the GNU GPLv3+ License
# (see autogator/__init__.py for details)

"""
# Hardware

AutoGator has a number of optional hardware components that can be used to
control the motion of the PIC chip and other aspects of the system.

This module serves the following purposes:

* defines device interfaces for different types of hardware, such as lasers,
  motors, and other devices  
* defines concrete implementations of interfaces for specific hardware
* tracks the "concept of motion" of the system as a whole
* centralizes control of an AutoGator instance's available resources
"""

import concurrent.futures
import importlib
import logging
from pathlib import Path
import time
from typing import Any, Dict, List, Tuple, Type, Union

import numpy as np
from pydantic import BaseModel, BaseSettings
try:
    from pyrolab.api import locate_ns, Proxy
    from pyrolab.drivers.scopes.rohdeschwarz import RTO
except:
    pass

from autogator.errors import UncalibratedStageError
from autogator.circuits import CircuitMap


log = logging.getLogger(__name__)


class HardwareDevice:
    """
    Abstract base class for hardware devices.

    This class is used to define the lowest level interface for hardware
    devices. It is not intended to be used directly, but rather to be
    subclassed by specific hardware devices.

    AutoGator hardware devices mainly interact with drivers provided by
    external libraries. AutoGator does not aim to provide any of the low-level
    interfacing with hardware devices, but rather implements a higher-level
    interface that abstracts the underlying hardware drivers. In this way, the
    same AutoGator motion and control routines can be used to control different
    hardware with different APIs, simply because they must implement the same
    AutoGator interface.

    AutoGator hardware devices keep a reference to the underlying hardware
    driver. While no AutoGator routine will make use of custom functionality,
    user-implemented [`Experiment`][autogator.experiments.Experiment] classes
    which access the Stage object may want to call functions on the driver
    directly.

    Attributes
    ----------
    driver : object
        A placeholder for a driver object. All objects provide the ability to
        directly access the underlying driver object.
    """
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
    def __init__(self, name: str, axis=Tuple[float, float, float]) -> None:
        self.name = name
        self.axis = axis

    def move_to(self, position: float) -> None:
        """
        Move the motor to a position.

        Parameters
        ----------
        position : float
            The position to move the motor to.
        """
        log.info(f"Moving {self.name} to {position}")

    def move_by(self, distance: float) -> None:
        """
        Move the motor by a distance.

        Some motors have the capability for more accurate "jogs." This function
        exists to support that capability. Motors that don't have this
        capability can imitate its effects by simply using
        [`move_to()`][autogator.hardware.LinearStageBase.move_to].

        Parameters
        ----------
        distance : float
            The distance to move the motor. A positive value will move the
            motor forward, and a negative value will move the motor backwards.
        """
        log.info(f"Moving {self.name} by {distance}")

    def move_cont(self, direction: float) -> None:
        """
        Move the motor continuously in the specified direction.

        A positive value for direction will move the motor in its forward
        sense. A negative value will move the motor in its reverse sense. The
        magnitude of direction can optionally correlate with the speed of the
        move, if the motor supports it.

        Parameters
        ----------
        direction : float
            The direction and velocity with which to start moving the motor.
        """
        log.info(f"Moving {self.name} continuously in {direction}")

    def stop(self) -> None:
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

    def home(self) -> None:
        """
        Move the motor to its home position, if supported.
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
    
    def close(self) -> None:
        """
        This should close the connection to the cube

        Returns
        -------
        None
        """
        log.info(f"Closing LinearStageBase {self.name}")
        
    



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
    def __init__(self, name: str, axis=Tuple[float, float, float]) -> None:
        self.name = name
        self.axis = axis

    def move_to(self, position: float) -> None:
        """
        Move the motor to a position.

        Parameters
        ----------
        position : float
            The position to move the motor to.
        """
        log.info(f"Moving {self.name} to {position}")

    def move_by(self, distance: float) -> None:
        """
        Move the motor by a distance.

        Some motors have the capability for more accurate "jogs." This function
        exists to support that capability. Motors that don't have this
        capability can imitate its effects by simply using
        [`move_to()`][autogator.hardware.RotationalStageBase.move_to].

        Parameters
        ----------
        distance : float
            The distance to move the motor.
        """
        log.info(f"Moving {self.name} by {distance}")

    def move_cont(self, direction: float) -> None:
        """
        Move the motor continuously in the specified direction.

        A positive value for direction will move the motor in its forward
        sense. A negative value will move the motor in its reverse sense. The
        magnitude of direction can optionally correlate with the speed of the
        move, if the motor supports it.

        Parameters
        ----------
        direction : float
            The direction and velocity with which to start moving the motor.
        """
        log.info(f"Moving {self.name} continuously in {direction}")

    def stop(self) -> None:
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

    def home(self) -> None:
        """
        Move the motor to its home position, if supported.
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
    
    def close(self) -> None:
        """
        This should close the connection to the cube

        Returns
        -------
        None
        """
        log.info(f"Closing RotationalStageBase {self.name}")


class DataAcquisitionUnitBase(HardwareDevice):
    """
    A data acquisition unit.

    This class is used to control a data acquisition unit.

    Parameters
    ----------
    name : str
        The name of the data acquisition unit.
    """
    def __init__(self, name: str) -> None:
        self.name = name

    def measure(self) -> Any:
        """
        Takes a single-shot measurement.

        Returns
        -------
        Any
            The measured data.
        """
        log.info(f"Measuring {self.name}")

    def acquire(self) -> None:
        """
        Asynchronous command to begin acquiring data.

        This method should acquire data from the data acquisition unit.
        """
        log.info(f"Acquiring data from {self.name}")

    def get_data(self) -> Any:
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
    Base class for laser devices.

    This class is used to control a laser.

    Parameters
    ----------
    name : str
        The name of the laser.
    """
    def __init__(self, name: str) -> None:
        self.name = name

    def on(self) -> None:
        """
        Turn the laser on.
        """
        log.info(f"Turning {self.name} on")

    def off(self) -> None:
        """
        Turn the laser off.
        """
        log.info(f"Turning {self.name} off")

    def power(self, power: float) -> None:
        """
        Set the power of the laser.

        Parameters
        ----------
        power : float
            The power of the laser.
        """
        log.info(f"Setting power of {self.name} to {power}")

    def wavelength(self, wavelength: float) -> None:
        """
        Set the wavelength of the laser.

        Parameters
        ----------
        wavelength : float
            The wavelength of the laser.
        """
        log.info(f"Setting wavelength of {self.name} to {wavelength}")

    def sweep(self) -> None:
        """
        Sweep the laser.
        """
        log.info(f"Sweeping {self.name}")


class CameraBase(HardwareDevice):
    """
    Base class for camera devices.

    This class is used to control a camera.

    Parameters
    ----------
    name : str
        The name of the camera.
    """
    def __init__(self, name: str) -> None:
        self.name = name

    def get_frame(self) -> Any:
        """
        Take a picture.

        This method should take a picture from the camera.
        """
        log.info(f"Taking picture from {self.name}")


class GenericPyroLabDevice(HardwareDevice):
    """
    A class that passes all function calls on to the PyroLab driver.

    This class is used to pass all function calls and attribute requests on to
    a nonstandard PyroLab driver. This is useful for devices that are not
    implemented or described by the standard AutoGator API, such as custom,
    homebuilt hardware.

    Parameters
    ----------
    pyroname : str
        The name of the PyroLab object as registered with the nameserver.
    ns_host : str, optional
        The hostname of the PyroLab nameserver (default "localhost").
    ns_port : int, optional
        The port of the PyroLab nameserver (default "9090").
    """
    def __init__(self, pyroname: str = "", ns_host: str = "localhost", ns_port: int = 9090) -> None:
        super().__init__(pyroname)
        with locate_ns(host=ns_host, port=ns_port) as ns:
            self.driver = Proxy(ns.lookup(pyroname))
            self.driver.autoconnect()

    def __getattr__(self, __name: str) -> Any:
        return self.driver.__getattr__(__name)


class Stage:
    """
    Singleton-like class that centralizes access to all hardware devices. 

    If you know a certain stage axis supports more complex functions, you can
    access the object directly using the ``driver`` attribute, e.g.:
    
    ``` python
    x_motor = stage.x.driver
    x_motor.unexposed_function()
    ```

    Additionally, any "auxiliary" devices can also be directly accessed as 
    attributes, e.g.:

    ``` python
    daq = stage.daq
    daq.measure()
    daq.driver.unexposed_function()
    ```

    Parameters
    ----------
    x : LinearStageBase
        The x-axis stage.
    y : LinearStageBase
        The y-axis stage.
    z : LinearStageBase
        The z-axis stage.
    theta : RotationalStageBase
        The theta-axis stage.
    phi : RotationalStageBase
        The phi-axis stage.
    psi : RotationalStageBase
        The psi-axis stage.
    calibration_matrix : np.ndarray, optional
        The calibration matrix for the stage. Converts from motor coordinates
        to GDS coordinates. If not provided, some stage functionality
        will be unavailable.
    loaded_position : np.ndarray, optional
        A default "goto" position for positioning the stage under the fiber
        array and camera.
    unloaded_position : np.ndarray, optional
        A default "goto" position for pulling the stage away from the fiber
        array and camera, enabling easier access to the sample for switching
        chips, etc.
    **auxiliaries : HardwareDevice, optional
        Any other devices that are not part of the standard stage. Keyword will
        be used as device attribute, and can be retrieved from the stage
        using that same name. Argument is the device object. Useful for 
        specifying more instruments, such as a scope, DAQ, or microscope lamp
        controller.
    """    
    def __init__(
        self, 
        x: LinearStageBase = None, 
        y: LinearStageBase = None, 
        z: LinearStageBase = None, 
        theta: RotationalStageBase = None, 
        phi: RotationalStageBase = None, 
        psi: RotationalStageBase = None, 
        calibration_matrix: np.ndarray = None, 
        loaded_position: List[float] = [None, None, None, None, None, None],
        unloaded_position: List[float] = [None, None, None, None, None, None],
        **auxiliaries: HardwareDevice,
    ) -> None:
        self.x = x
        self.y = y
        self.z = z
        self.theta = theta
        self.phi = phi
        self.psi = psi

        self.calibration_matrix = calibration_matrix
        self.loaded_position = loaded_position
        self.unloaded_position = unloaded_position
        self.auxiliaries = auxiliaries

        # TODO: Implement?
        # self._last_calibrated = None
        # self._last_homed = None

    def __getattr__(self, name) -> Any:
        if name in self.auxiliaries:
            return self.auxiliaries[name]
        else:
            raise AttributeError(f"'Stage' object has no attribute '{name}'")

    def load_calibration_matrix(self, filename: Union[str, Path]) -> None:
        """
        Load a conversion matrix from a file.

        Parameters
        ----------
        filename : str
            The path to the file containing the conversion matrix.

        Raises
        ------
        FileNotFoundError
            If the file does not exist.
        """
        if isinstance(filename, str):
            filename = Path(filename)
        if not filename.exists():
            raise FileNotFoundError(f"File {filename} does not exist.")
        self.calibration_matrix = np.loadtxt(filename)

    def save_calibration_matrix(self, filename: str) -> None:
        """
        Saves a conversion matrix to a file.

        Parameters
        ----------
        filename : str
            The path to the file to save the conversion matrix to.
        """
        np.savetxt(filename, self.calibration_matrix)

    @property
    def motors(self) -> list:
        """
        Returns a list of all motors, ordered [x, y, z, theta, phi, psi].
        """
        return [self.x, self.y, self.z, self.theta, self.phi, self.psi]

    def set_position(self, *, pos: List[float] = [], x: float = None, y: float = None, z: float = None, theta: float = None, phi: float = None, psi: float = None) -> None:
        """
        Set the position of the stage in real world units.

        Any unspecified parameters won't be moved. All parameters are
        keyword-only (no positional parameters accepted).

        Parameters
        ----------
        pos : list, optional
            The position to move to as a 6-list of floats, matching the format
            of ``Stage.get_position``. If specified, all other parameters are
            ignored.
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
        if not pos:
            pos = [x, y, z, theta, phi, psi]
        commands = [cmd for cmd in zip(self.motors, pos) if cmd[1] is not None]

        with concurrent.futures.ThreadPoolExecutor(max_workers=len(commands)) as executor:
            # Start the load operations and mark each future with its URL
            future_to_cmd = {}
            for motor, pos in commands:
                future_to_cmd[executor.submit(motor.move_to, pos)] = motor
                time.sleep(0.01) # Space out simultaneous calls to potentially shared DLLs
            for future in concurrent.futures.as_completed(future_to_cmd):
                motor = future_to_cmd[future]
                try:
                    driver = future.result()
                except Exception as exc:
                    print(f'{motor} generated an exception: {exc}')
                    log.exception(exc)

    def jog_position(self, *, pos: List[float] = [], x=None, y=None, z=None, theta=None, phi=None, psi=None) -> None:
        """
        Set the position of the stage in real world units.

        Any unspecified parameters won't be moved. All parameters are
        keyword-only (no positional parameters accepted).

        Parameters
        ----------
        pos : list, optional
            The position to move to as a 6-list of floats, matching the format
            of ``Stage.get_position``. If specified, all other parameters are
            ignored.
        x : float, optional
            The x jog step.
        y : float, optional
            The y jog step.
        z : float, optional
            The z jog step.
        theta : float, optional
            The theta jog step.
        phi : float, optional
            The phi jog step.
        psi : float, optional
            The psi jog step.
        """
        if not pos:
            pos = [x, y, z, theta, phi, psi]
        commands = [cmd for cmd in zip(self.motors, pos) if cmd[1] is not None]
        for motor, pos in commands:
            if motor:
                motor.move_by(pos)

    def set_position_gds(self, x: float, y: float) -> None:
        """
        Set the position of the stage in GDS coordinates.

        Only supports 2D commands, i.e. (x, y) coordinates.

        Parameters
        ----------
        x : float
            The x coordinate.
        y : float
            The y coordinate.

        Raises
        ------
        UncalibratedStageError
            If the stage is not calibrated. GDS position cannot be set without
            first calibrating the stage.
        """
        if self.calibration_matrix is None:
            raise UncalibratedStageError("Stage is not calibrated (no conversion matrix set), cannot set position in GDS coordinates")

        gds_pos = np.array([[x], [y], [1]])
        stage_pos = self.calibration_matrix @ gds_pos

        self.set_position(x=stage_pos[0, 0], y=stage_pos[1, 0])
        actual = self.get_position()
        log.info(f"CMD: ({stage_pos[0,0], stage_pos[1,0]}), ACT: ({actual[0], actual[1]}), ERR: ({stage_pos[0,0] - actual[0], stage_pos[1,0] - actual[1]})")

    def get_position(self) -> List[float]:
        """
        Returns the current position of the stage.

        Returns
        -------
        List[float]
            A list of the current position of each motor as a six-vector of
            floats. The order is [x, y, z, theta, phi, psi].
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

        This method places the stage in the loaded position.
        """
        log.info("Loading stage")
        self.set_position(*self.loaded_position)

    def unload(self):
        """
        Unload the stage.

        This method places the stage in the unloaded position.
        """
        log.info("Unloading stage")
        self.set_position(*self.unloaded_position)


class HardwareConfiguration(BaseSettings):
    """
    A class for storing the hardware configurations of an arbitrary driver.

    Attributes
    ----------
    module : str, optional
        The name of the module containing the driver (default
        "autogator.hardware"). AutoGator supports external drivers that 
        implement AutoGator's HardwareDevice interface.
    classname : str
        The name of the class implementing the driver, to be dynamically
        loaded from the module.
    parameters : dict, optional
        A dictionary of initialization parameters to pass to the driver.
        It is therefore best for drivers to have keyword-only initialization
        parameters.
    """
    module: str = "autogator.hardware"
    classname: str = ""
    parameters: Dict[str, Any] = {}

    def get_object(self) -> Type[HardwareDevice]:
        """
        Constructs and returns the instantiated driver object.

        Returns
        -------
        Type[HardwareDevice]
            The driver object.
        """
        log.debug(f"Attempting to load '{self.module}.{self.classname}'")
        try:
            mod = importlib.import_module(self.module)
            log.debug("Module found...")
            obj: HardwareDevice = getattr(mod, self.classname)
            log.debug("Class found...")
        except Exception as e:
            log.critical(e)
            raise e
        
        return obj(**self.parameters)


class StageConfiguration(BaseSettings):
    """
    The persisted stage configuration. Typically stored as a JSON file.

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
    calibration_matrix : str
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
    calibration_matrix: str = ""
    loaded_position: List[Any] = [None, None, None, None, None, None]
    unloaded_position: List[Any] = [None, None, None, None, None, None]
    auxiliaries: Dict[str, HardwareConfiguration] = {}

    def get_stage(self) -> Stage:
        """
        Constructs and returns the instantiated stage object.

        Returns
        -------
        Stage
            The stage object.
        """
        cmatfile = Path(self.calibration_matrix)
        calibration_matrix = np.loadtxt(cmatfile) if cmatfile.is_file() else None

        log.info("Loading stage objects...")
        names = ["x", "y", "z", "theta", "phi", "psi"]
        configs = [self.x, self.y, self.z, self.theta, self.phi, self.psi]
        to_load = {name: config for name, config in zip(names, configs) if config}
        to_load.update(self.auxiliaries)
        loaded = {}

        ###################################
        for name, config in to_load.items():
            log.info(f"Loading {name} stage...")
            max_retries = 10
            count = 0
            status = "failed"
            while count < max_retries:
                try:
                    driver = config.get_object()
                    if (count > 8):
                        time.sleep(2)           
                    status = "success"
                    break
                except:
                    #log.info("Failed to connect to", name, "trying again")
                    count += 1
                    print(count)

            # Space out simultaneous calls to potentially shared DLLs
            if (status == "success"):
                loaded[name] = driver
            else:
                print(f"failed to connect after {max_retries} attempts")
        ###################################


        # # Laod all stage objects in parallel, in case they are slow
        # # Code adapted from https://docs.python.org/3/library/concurrent.futures.html#threadpoolexecutor-example
        # with concurrent.futures.ThreadPoolExecutor(max_workers=len(configs)) as executor:
        #     # Start the load operations and mark each future with its URL
        #     future_to_config = {}
        #     for name, config in to_load.items():
        #         log.info(f"Loading {name} stage...")
        #         future_to_config[executor.submit(config.get_object)] = name
        #         # Space out simultaneous calls to potentially shared DLLs
        #         time.sleep(3)
        #     for future in concurrent.futures.as_completed(future_to_config):
        #         name = future_to_config[future]
        #         try:
        #             driver = future.result()
        #         except Exception as exc:
        #             print(f'{name} generated an exception: {exc}')
        #             log.exception(exc)
        #         else:
        #             loaded[name] = driver

        log.info("Stage objects loaded.")
        return Stage(
            **loaded,
            calibration_matrix = calibration_matrix,
            loaded_position = self.loaded_position,
            unloaded_position = self.unloaded_position,
        )


###############################################################################


class Z825BLinearStage(LinearStageBase):
    """
    A linear motor.

    Parameters
    ----------
    pyroname : str
        The name of the PyroLab object as registered with the nameserver.
    ns_host : str, optional
        The hostname of the PyroLab nameserver (default "localhost").
    ns_port : int, optional
        The port of the PyroLab nameserver (default "9090").
    """
    def __init__(self, pyroname: str = "", ns_host: str = "localhost", ns_port: int = 9090) -> None:
        super().__init__(pyroname)
        with locate_ns(host=ns_host, port=ns_port) as ns:
            self.driver = Proxy(ns.lookup(pyroname))
            self.driver.autoconnect()
        self._step_size = None

    @property
    def step_size(self) -> float:
        """The jog step size in mm."""
        return self._step_size

    @step_size.setter
    def step_size(self, step_size: float) -> None:
        if step_size != self._step_size:
            self.driver._pyroClaimOwnership()
            self.driver.jog_step_size = step_size
            self._step_size = step_size

    def move_to(self, position: float) -> None:
        """
        Moves to a new position.

        This motor adjusts for backlash; a given position will always be
        approached from the "negative" direction. That may require overshooting
        the commanded position in order to always approach it again from a
        consistent direction.

        If stepping in short steps, it is therefore most efficient to step from
        negative to positive values to avoid backlash adjustments on each step.

        Parameters
        ----------
        position : float
            The new position to move to.
        """
        self.driver._pyroClaimOwnership()
        if self._requires_backlash_adjustment(position):
            self.driver.move_to(position - (self.driver.backlash * 1.5))
        self.driver.move_to(position)

    def move_by(self, distance: float) -> None:
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

    def stop(self) -> None:
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

    def home(self) -> None:
        """
        Home the motor.
        """
        self.driver._pyroClaimOwnership()
        self.driver.go_home()

    def status(self) -> int:
        """
        Returns a nonzero value if the motor is busy.
        """
        pass

    def close(self) -> None:
        """
        This should close the connection to the cube

        Returns
        -------
        None
        """
        log.info(f"Closing LinearStageBase {self.name}")
        self.driver._pyroClaimOwnership()
        self.driver.close()


class PRM1Z8RotationalStage(RotationalStageBase):
    """
    A rotational motor.

    Parameters
    ----------
    pyroname : str
        The name of the PyroLab object as registered with the nameserver.
    ns_host : str, optional
        The hostname of the PyroLab nameserver (default "localhost").
    ns_port : int, optional
        The port of the PyroLab nameserver (default "9090").
    """
    def __init__(self, pyroname: str = "", ns_host: str = "localhost", ns_port: int = 9090) -> None:
        super().__init__(pyroname)
        with locate_ns(host=ns_host, port=ns_port) as ns:
            self.driver = Proxy(ns.lookup(pyroname))
            self.driver.autoconnect()
        self._step_size = None

    @property
    def step_size(self) -> float:
        """The jog step size in mm."""
        return self._step_size

    @step_size.setter
    def step_size(self, step_size: float) -> None:
        if step_size != self._step_size:
            self.driver._pyroClaimOwnership()
            self.driver.jog_step_size = step_size
            self._step_size = step_size

    def move_to(self, position: float) -> None:
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

    def move_by(self, distance: float) -> None:
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

    def stop(self) -> None:
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

    def home(self) -> None:
        """
        Home the motor.
        """
        self.driver._pyroClaimOwnership()
        self.driver.go_home()

    def status(self) -> int:
        """
        Returns a nonzero value if the motor is busy.
        """
        pass

    def close(self) -> None:
        """
        This should close the connection to the cube

        Returns
        -------
        None
        """
        log.info(f"Closing RotationalStageBase {self.name}")
        self.driver._pyroClaimOwnership()
        self.driver.close()


class TSL550Laser(LaserBase):
    """
    A laser.

    Parameters
    ----------
    pyroname : str
        The name of the PyroLab object as registered with the nameserver.
    ns_host : str, optional
        The hostname of the PyroLab nameserver (default "localhost").
    ns_port : int, optional
        The port of the PyroLab nameserver (default "9090").
    """
    def __init__(self, pyroname: str = "", ns_host: str = "localhost", ns_port: int = 9090):
        super().__init__(pyroname)
        with locate_ns(host=ns_host, port=ns_port) as ns:
            self.driver = Proxy(ns.lookup(pyroname))
            self.driver.autoconnect()

    def on(self, block=False) -> None:
        """
        Turn on the laser.

        If the laser diode is off, there is a warm-up time before the laser
        diode is ready. If block is True, this function will block until the
        warm-up time is complete.

        Parameters
        ----------
        block : bool, optional
            Whether to block until the warm-up time is complete (default False).
        """
        self.driver._pyroClaimOwnership()
        if self.driver.status()[0] != '-':
            self.driver.on()
            if block:
                while self.driver.status()[0] != '-':
                    time.sleep(5.0)    
        self.driver.open_shutter()

    def off(self, diode: bool = True) -> None:
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

    def power(self, power: float) -> None:
        """
        Sets the laser power in dBm.

        Parameters
        ----------
        power : float
            The power to set the laser to.
        """
        self.driver._pyroClaimOwnership()
        self.driver.power_dBm(power)

    def wavelength(self, wavelength: float) -> None:
        """
        Sets the laser wavelength in nm.

        Parameters
        ----------
        wavelength : float
            The wavelength to set the laser to.
        """
        self.driver._pyroClaimOwnership()
        self.driver.wavelength(wavelength)

    def sweep(self, num: int = 1) -> None:
        """
        Starts the configured wavelength sweep.

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
        self, continuous: bool = True, twoway: bool = True, trigger: bool = False, const_freq_step: bool = False
    ) -> None:
        """
        Sets the sweep mode.

        Parameters
        ----------
        continuous : bool
            Continuous (``True``, default) or stepwise (``False``).
        twoway : bool
            Two-way (``True``, default) or one-directional with reset
            (``False``).
        trigger : bool
            Start on external trigger (defaults to ``False``).
        const_freq_step : bool
            Constant frequency interval, requires stepwise mode (defaults to
            ``False``).
        """
        self.driver._pyroClaimOwnership()
        self.driver.sweep_set_mode(
            continuous=continuous,
            twoway=twoway,
            trigger=trigger,
            const_freq_step=const_freq_step,
        )

    def set_trigger(self, mode: str, step: float) -> None:
        """
        Enables trigger output.

        The output trigger can be set to fire at the start of a wavelength
        sweep, at the end of a sweep, or at a fixed step. Valid step range is
        0.004 - 160 nm with a minimum step of 0.0001 nm.

        Parameters
        ----------
        mode : str
            The trigger mode. One of: “None”, “Stop”, “Start”, “Step”.
        step : float
            The trigger step size, in nanometers.
        """
        self.driver._pyroClaimOwnership()
        self.driver.trigger_enable_output()
        triggerMode = self.driver.trigger_set_mode(mode)
        triggerStep = self.driver.trigger_step(step)
        return triggerMode, triggerStep

    def wavelength_logging(self) -> None:
        """
        Downloads the wavelength log.

        Returns
        -------
        list
            The last wavelength log.
        """
        self.driver._pyroClaimOwnership()
        return self.driver.wavelength_logging()

    
class RohdeSchwarzOscilliscope(DataAcquisitionUnitBase):
    """
    A Rohde-Schwarz oscilliscope simplified interface.

    Parameters
    ----------
    name : str
        An name for the oscilloscope.
    address : str
        The IP address (or other valid identifier, see PyroLab's documentation)
        of the oscilloscope.
    hislip : str, optional
        Whether to use the HiSLIP protocol or not (default False) (not
        supported unless you are using the NI VISA driver).
    timeout : float, optional
        The timeout for the connection in milliseconds (default 30000.0).
    """
    def __init__(self, name: str, address: str, hislip: bool = False, timeout: float = 30000.0):
        super().__init__(name)
        self.driver = RTO()
        self.driver.connect(address, hislip=hislip, timeout=timeout)

    def measure(self) -> float:
        """
        Performs a single-shot measurement, if configured.

        See PyroLab's documentation for more information. Requires first 
        configuring the measurement with ``set_auto_measurement()``.

        Returns
        -------
        float
            The measured value.
        """
        return self.driver.measure()

    def acquire(self, timeout: float = -1) -> float:
        """
        Asynchronous command that starts acquisition.

        Parameters
        ----------
        timeout : float, optional
            The timeout for the acquisition in milliseconds (default -1). If
            not modified, default timeout is used. Can be changed for this
            single function call, after which it is reset to the original
            value.
        """
        self.driver.acquire(timeout=timeout)

    def get_data(self, channel: int) -> List[float]:
        """
        Gets the data from the specified channel.
        
        Parameters
        ----------
        channel : int
            The channel to retrieve the data from.
        """
        # TODO: Convert this to binary instead of ascii, which is faster?
        # TODO: Verify return type.
        return self.driver.get_data(channel)

    def wait_for_device(self) -> None:
        """
        Waits for the device to be ready (finished with all previous commands).

        This is a blocking call.
        """
        self.driver.wait_for_device()

    def set_channel(self, channel: int, range: float = 0.5, coupling: str = "DCLimit", position: float = 0.0) -> None:
        """
        Sets the channel parameters.

        Parameters
        ----------
        channel : int
            The channel to set.
        range : float
            Sets the voltage range across the 10 vertical divisions of the
            diagram in V/div. Default is 0.5.
        coupling : str
            Selects the connection of the indicated channel signal. Valid
            values are “DC” (direct connection with 50 ohm termination),
            “DCLimit” (direct connection with 1M ohm termination), or “AC”
            (connection through DC capacitor). Default is "DCLimit".
        position : float, optional
            Sets the vertical position of the indicated channel as a graphical
            value. Valid range is [-5, 5] in increments of 0.01 (units is
            “divisions”). Default is 0.
        """
        self.driver.set_channel(channel, range=range, coupling=coupling, position=position)

    def set_channel_for_auto_measurement(
        self,
        channel: int,
        range: float = 0.5,
        coupling: str = "DCLimit",
        position: float = 0,
        timescale: float = 10e-9,
    ) -> None:
        """
        Sets the channel parameters for auto measurement.

        Parameters
        ----------
        channel : int
            The channel to set.
        range : float
            Sets the voltage range across the 10 vertical divisions of the
            diagram in V/div. Default is 0.5.
        coupling : str
            Selects the connection of the indicated channel signal. Valid
            values are “DC” (direct connection with 50 ohm termination),
            “DCLimit” (direct connection with 1M ohm termination), or “AC”
            (connection through DC capacitor). Default is "DCLimit".
        position : float
            Sets the vertical position of the indicated channel as a graphical
            value. Valid range is [-5, 5] in increments of 0.01 (units is
            “divisions”). Default is 0.
        timescale : float
            The time (in seconds) per division. Valid range is from 25e-12 to
            10000 (RTO) | 5000 (RTE) in increments of 1e-12. Default is 10e-9.
        """
        self.driver.set_timescale(timescale)
        self.set_channel(channel, range=range, coupling=coupling, position=position)
        self.driver.set_auto_measurement(source="C" + str(channel) + "W1")
        self.wait_for_device()

    def set_acquisition_settings(self, sample_rate: float, duration: float) -> None:
        """
        Sets the acquisition settings.

        Parameters
        ----------
        sample_rate : float
            Sample rate of device in Sa/s. Range is 2 to 20e+12 in increments
            of 1.
        duration : float
            Length of acquisition in seconds.
        """
        self.driver.acquisition_settings(sample_rate=sample_rate, duration=duration)

    def set_edge_trigger(self, trigger_channel: int, trigger_level: int) -> None:
        """
        Sets a trigger channel and level.

        Parameters
        ----------
        trigger_channel : int
            The channel to trigger on.
        trigger_level : int
            Voltage threshold for positive slope edge trigger.
        """
        self.driver.edge_trigger(trigger_channel, trigger_level)
