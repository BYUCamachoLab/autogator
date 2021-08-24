"""
Interfaces
----------

Collection of interfaces to create the objects used throughout autogator. 
Each function needs to be defined inside the interface class in order for 
autogator to work. Examples of instantiations of interfaces into classes can 
be found below.
"""
from pyrolab.api import locate_ns, Proxy
from pyrolab.drivers.motion.z825b import Z825B
from pyrolab.drivers.motion.prm1z8 import PRM1Z8
from pyrolab.drivers.scopes.rohdeschwarz import RTO


class ILinearMotor:
    """
    Interface for linearly moving motors in autogator setup.
    """
    def move_by(self, direction: str = "", step_size: float = None):
        """
        Moves motor one jog in specified direction and step_size.

        .. note:: If step_size isn't specified it keeps the last step_size used.
        ...

        Parameters
        ----------
        direction: str, default=""
            The direction (forward or backward) that the motor will move.
        step_size: float, default=None
            The size of the step the motor will use in mm.
        """
        pass

    def move_to(self, position: float):
        """
        Moves motor to specified position in stage coordinates.
        ...

        Parameters
        ----------
        position: float
            The position in stage coordinates the motor will move to.
        """
        pass

    def step_size(self, step_size: float = None) -> float:
        """
        If step_size is specified changes motor parameter. Returns current step_size after potential change.
        ...

        Parameters
        ----------
        step_size: float
            The step_size to set motor movement to.

        Returns
        -------
        step_size: float
            The step_size the motor is currently set to.
        """
        pass

    def move_cont(self, direction: str):
        """
        Starts continuous movement of motor.
        ...

        Parameters
        ----------
        direction: str
            The direction (foward or backward) the motor will move in.
        """
        pass

    def stop(self):
        """
        Stops motor movement.
        """
        pass

    def get_position(self) -> float:
        """
        Returns motors current position in stage coordinates.
        ...

        Returns
        -------
        position: float
            Motors current position in stage coordinates.
        """
        pass

    def home(self):
        """
        Moves motor into minimum home position and resets position to 0.
        """
        pass


class IRotationalMotor:
    """
    Interface for rotationally moving motors in autogator setup.
    """
    def move_by(self, direction: str = "", step_size: float = None):
        """
        Moves motor one jog in specified direction and step_size.

        .. note:: If step_size isn't specified it keeps the last step_size used.
        ...

        Parameters
        ----------
        direction: str, default=""
            The direction (forward or backward) that the motor will move.
        step_size: float, default=None
            The size of the step the motor will use in mm.
        """
        pass

    def move_to(self, position: float):
        """
        Moves motor to specified position in stage coordinates.
        ...

        Parameters
        ----------
        position: float
            The position in stage coordinates the motor will move to.
        """
        pass

    def step_size(self, step_size: float = None) -> float:
        """
        If step_size is specified changes motor parameter. Returns current step_size after potential change.
        ...

        Parameters
        ----------
        step_size: float
            The step_size to set motor movement to.

        Returns
        -------
        step_size: float
            The step_size the motor is currently set to.
        """
        pass

    def move_cont(self, direction: str):
        """
        Starts continuous movement of motor.
        ...

        Parameters
        ----------
        direction: str
            The direction (foward or backward) the motor will move in.
        """
        pass

    def stop(self):
        """
        Stops motor movement.
        """
        pass

    def get_position(self) -> float:
        """
        Returns motors current position in stage coordinates.
        ...

        Returns
        -------
        position: float
            Motors current position in stage coordinates.
        """
        pass

    def home(self):
        """
        Moves motor into minimum home position and resets position to 0.
        """
        pass


class IOscilliscope:
    def measure(self):
        pass

    def set_channel(self, channel: int, range: float, coupling: str, position: float):
        pass

    def set_channel_for_measurement(
        self,
        channel: int,
        range: float,
        coupling: str,
        position: float,
        timescale: float,
    ):
        pass

    def set_acquisition_settings(self, sample_rate: float, duration: float):
        pass

    def set_edge_trigger(self, trigger_channel: int, trigger_level: int):
        pass

    def acquire(self, timeout: float):
        pass

    def wait_for_device(self):
        pass

    def screenshot(self, output_directory: str, filename: str):
        pass

    def get_data(self, channel: int):
        pass


class ILaser:
    def start(self):
        pass

    def on(self):
        pass

    def power_dBm(self, power_dBm: float):
        pass

    def open_shutter(self):
        pass

    def sweep_set_mode(
        self, continuous: bool, twoway: bool, trigger: bool, const_freq_step: bool
    ):
        pass

    def set_trigger(self, mode: str, step: float):
        pass

    def sweep_wavelength(self, wl_start: float, wl_stop: float, duration: float):
        pass

    def wavelength_logging(self):
        pass


class Z825BLinearMotor(ILinearMotor):
    def __init__(self, motor_info):
        self._pyro_object = None
        self._last_step_size = None
        if motor_info["location"] == "remote":
            self.from_pyro_server(motor_info["nameserver"], motor_info["remotename"])
        elif motor_info["location"] == "local":
            self.from_local_server(motor_info["localname"])
        else:
            raise ValueError("Location of motor error")

    def from_pyro_server(self, name_server: str = "", pyro_name: str = ""):
        ns = locate_ns(name_server)
        available_device_list = ns.list()
        if pyro_name in available_device_list.keys():
            self._pyro_object = Proxy(ns.lookup(pyro_name))
            self._pyro_object.autoconnect()
        else:
            raise ValueError("Object name not found on server")

    def from_local_server(self, serialno: str = ""):
        self._pyro_object = Z825B()
        self._pyro_object.connect(serialno=serialno)

    def move_by(self, direction: str = "", step_size: float = None):
        if step_size is not None:
            self.step_size(step_size)
        self._pyro_object.jog(direction)

    def requires_backlash_adjustment(self, position: float) -> bool:
        if position < self.get_position():
            return True
        return False

    def move_to(self, position: float):
        if self.requires_backlash_adjustment(position):
            self._pyro_object.move_to(position - (self._pyro_object.backlash * 1.5))
        self._pyro_object.move_to(position)

    def step_size(self, step_size: float = None) -> float:
        if step_size is not None:
            if step_size != self._last_step_size:
                self._pyro_object.jog_step_size = step_size
                self._last_step_size = step_size
        return self._pyro_object.jog_step_size

    def move_cont(self, direction: str):
        self._pyro_object.move_continuous(direction)

    def stop(self):
        self._pyro_object.stop()

    def get_position(self) -> float:
        return self._pyro_object.get_position()

    def home(self):
        self._pyro_object.go_home()


class PRM1Z8RotationalMotor(IRotationalMotor):
    def __init__(self, motor_info):
        self._pyro_object = None
        self._last_step_size = None
        if motor_info["location"] == "remote":
            self.from_pyro_server(motor_info["nameserver"], motor_info["remotename"])
        elif motor_info["location"] == "local":
            self.from_local_server(motor_info["localname"])
        else:
            raise ValueError("Location of motor error")

    def from_pyro_server(self, name_server: str = "", pyro_name: str = ""):
        ns = locate_ns(name_server)
        available_device_list = ns.list()
        if pyro_name in available_device_list.keys():
            self._pyro_object = Proxy(ns.lookup(pyro_name))
            self._pyro_object.autoconnect()
        else:
            raise ValueError("Object name not found on server")

    def from_local_server(self, serialno: str = ""):
        self._pyro_object = Z825B()
        self._pyro_object.connect(serialno=serialno)

    def move_by(self, direction: str = "", step_size: float = None):
        if step_size is not None:
            self.step_size(step_size)
        self._pyro_object.jog(direction)

    def requires_backlash_adjustment(self, position: float) -> bool:
        if position < self.get_position():
            return True
        return False

    def move_to(self, position: float):
        if self.requires_backlash_adjustment(position):
            self._pyro_object.move_to(position - (self._pyro_object.backlash * 1.5))
        self._pyro_object.move_to(position)

    def step_size(self, step_size: float = None) -> float:
        if step_size is not None:
            if step_size != self._last_step_size:
                self._pyro_object.jog_step_size = step_size
                self._last_step_size = step_size
        return self._pyro_object.jog_step_size

    def move_cont(self, direction: str):
        self._pyro_object.move_continuous(direction)

    def stop(self):
        self._pyro_object.stop()

    def get_position(self) -> float:
        return self._pyro_object.get_position()

    def home(self):
        self._pyro_object.go_home()


class RohdeSchwarzOscilliscope(IOscilliscope):
    def __init__(self, scope_info):
        self._pyro_object = RTO(
            scope_info["IP"],
            protocol=scope_info["protocol"],
            timeout=scope_info["timeout"],
        )

    def measure(self):
        return self._pyro_object.measure()

    def wait_for_device(self):
        self._pyro_object.wait_for_device()

    def set_channel(self, channel: int, range: float, coupling: str, position: float):
        self._pyro_object.set_channel(
            channel, range=range, coupling=coupling, position=position
        )

    def set_channel_for_measurement(
        self,
        channel: int,
        range: float,
        coupling: str,
        position: float,
        timescale: float,
    ):
        self._pyro_object.set_timescale(timescale)
        self.set_channel(channel, range=range, coupling=coupling, position=position)
        self._pyro_object.set_auto_measurement(source="C" + str(channel) + "W1")
        self.wait_for_device()

    def set_acquisition_settings(self, sample_rate: float, duration: float):
        self._pyro_object.acquisition_settings(
            sample_rate=sample_rate, duration=duration
        )

    def set_edge_trigger(self, trigger_channel: int, trigger_level: int):
        self._pyro_object.edge_trigger(trigger_channel, trigger_level)

    def acquire(self, timeout: float):
        self._pyro_object.acquire(timeout=timeout)

    def screenshot(self, output_directory: str, filename: str):
        self._pyro_object.screenshot(output_directory + filename)

    def get_data(self, channel: int):
        return get_data(channel)


class TSL550Laser(ILaser):
    def __init__(self, laser_info):
        self._pyro_object = None
        ns = locate_ns(laser_info["nameserver"])
        available_device_list = ns.list()
        if laser_info["remotename"] in available_device_list.keys():
            self._pyro_object = Proxy(ns.lookup(laser_info["remotename"]))
        else:
            raise ValueError("Laser name not found on server")

    def start(self):
        self._pyro_object.start()

    def on(self):
        self._pyro_object.on()

    def power_dBm(self, power_dBm: float):
        self._pyro_object.power_dBm(power_dBm)

    def open_shutter(self):
        self._pyro_object.open_shutter()

    def sweep_set_mode(
        self, continuous: bool, twoway: bool, trigger: bool, const_freq_step: bool
    ):
        self._pyro_object.sweep_set_mode(
            continuous=continuous,
            twoway=twoway,
            trigger=trigger,
            const_freq_step=const_freq_step,
        )

    def set_trigger(self, mode: str, step: float):
        self._pyro_object.trigger_enable_output()
        triggerMode = self._pyro_object.trigger_set_mode(mode)
        triggerStep = self._pyro_object.trigger_set_step(step)
        return triggerMode, triggerStep

    def sweep_wavelength(self, wl_start: float, wl_stop: float, duration: float):
        self._pyro_object.sweep_wavelength(wl_start, wl_stop, duration)

    def wavelength_logging(self):
        self._pyro_object.wavelength_logging()
