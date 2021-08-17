from pyrolab.api import locate_ns, Proxy
from pyrolab.drivers.motion.z825b import Z825B
from pyrolab.drivers.motion.prm1z8 import PRM1Z8

class ILinearMotor:
    def move_by(self, direction: str = "", step_size: float = None):
        pass

    def move_to(self, position: float):
        pass

    def step_size(self, step_size: float = None) -> float:
        pass

    def move_cont(self, direction: str):
        pass

    def stop(self):
        pass

    def get_position(self):
        pass

    def home(self):
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

    def from_pyro_server(self, name_server:str = "", pyro_name:str = ""):
        ns = locate_ns(name_server)
        available_device_list = ns.list()
        if pyro_name in available_device_list.keys():
            self._pyro_object = Proxy(ns.lookup(pyro_name))
            self._pyro_object.autoconnect()
        else:
            raise ValueError('Object name not found on server')

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
        

class IRotationalMotor:
    def move_by(self, direction: str = "", step_size: float = None):
        pass

    def move_to(self, position: float):
        pass

    def step_size(self, step_size: float = None) -> float:
        pass

    def move_cont(self, direction: str):
        pass

    def stop(self):
        pass

    def get_position(self):
        pass

    def home(self):
        pass

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

    def from_pyro_server(self, name_server:str = "", pyro_name:str = ""):
        ns = locate_ns(name_server)
        available_device_list = ns.list()
        if pyro_name in available_device_list.keys():
            self._pyro_object = Proxy(ns.lookup(pyro_name))
            self._pyro_object.autoconnect()
        else:
            raise ValueError('Object name not found on server')

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