import keyboard
from enum import Enum, auto
import autogator.motion.motion as motpy

# This will be used to debounce the key press
SINGLE_MAX_ADC_COUNTER = 4

# These hotkeys are possible keyboard inputs that will result in the activation
# of the single press state machine
single_hotkeys = [
    "left arrow",
    "right arrow",
    "down arrow",
    "up arrow",
    "c",
    "x",
    "shift + j",
    "shift + g",
    "shift + k",
    "space",
    "o",
    "h",
]

# Some keys have different functionalities and so the motion.py commands will be different
# So I need to determine what type of key I'm working with
class key_type(Enum):
    MOTION = auto()
    SETTER = auto()
    INPUTLESS = auto()


# Single Press State Machine States
class single_states(Enum):
    INIT = auto()
    WAIT = auto()
    ADC_FILTER = auto()
    PRESS = auto()
    RELEASE = auto()


class single_action:
    def __init__(self, motion):
        self.init_printing = False
        self.wait_printing = False
        self.press_printing = False
        self.release_printing = False
        self.hotkey = None
        self.key_type = None
        self.motor = None
        self.direction = None
        self.motion = motion

    # Initializes the object
    def init(self):
        self.init_printing == False
        self.wait_printing = False
        self.press_printing = False
        self.release_printing = False
        self.hotkey = None
        self.key_type = None
        self.motor = None
        self.direction = None
        if self.init_printing == False:
            # print("Initialized")
            self.init_printing = True

    # This will wait for a key to be pressed and will reset variables
    def wait(self):
        self.init_printing = False
        self.release_printing = False
        self.hotkey = None
        self.key_type = None
        self.motor = None
        self.direction = None
        if self.wait_printing == False:
            # print("Waiting")
            self.wait_printing = True

    # This will be activated when a key is pressed
    def press(self):
        self.wait_printing = False
        if self.press_printing == False:
            # print("Pressing " + self.hotkey)
            self.process_key_type()
            self.press_printing = True

    # This will be actiavted upon release of the key
    def release(self):
        self.press_printing = False
        if self.release_printing == False:
            # print("Releasing " + self.hotkey)
            self.process_key_command()
            self.release_printing = True

    # This will see if any single press sm relevant keys were pressed and store the key
    def single_key_pressed(self) -> bool:
        output = False
        for hotkey in single_hotkeys:
            if keyboard.is_pressed(hotkey):
                output = True
                self.hotkey = hotkey
        return output

    # This will check to see if the same key is still being pressed
    def same_key_pressed(self) -> bool:
        return keyboard.is_pressed(self.hotkey)

    # Gets the key type so that the command can be proccessed later on
    def process_key_type(self):
        if (
            (self.hotkey == "left arrow")
            or (self.hotkey == "right arrow")
            or (self.hotkey == "down arrow")
            or (self.hotkey == "up arrow")
            or (self.hotkey == "c")
            or (self.hotkey == "x")
        ):
            self.key_type = key_type.MOTION
            if (self.hotkey == "left arrow") or (self.hotkey == "right arrow"):
                self.motor = self.motion.x_mot
                if self.hotkey == "left arrow":
                    self.direction = "backward"
                elif self.hotkey == "right arrow":
                    self.direction = "forward"
            elif (self.hotkey == "down arrow") or (self.hotkey == "up arrow"):
                self.motor = self.motion.y_mot
                if self.hotkey == "down arrow":
                    self.direction = "backward"
                elif self.hotkey == "up arrow":
                    self.direction = "forward"
            elif (self.hotkey == "c") or (self.hotkey == "x"):
                self.motor = self.motion.r_mot
                if self.hotkey == "c":
                    self.direction = "forward"
                elif self.hotkey == "x":
                    self.direction = "backward"
        elif (
            (self.hotkey == "shift + j")
            or (self.hotkey == "shift + g")
            or (self.hotkey == "shift + k")
        ):
            self.key_type = key_type.SETTER
        elif (self.hotkey == "space") or (self.hotkey == "o") or (self.hotkey == "h"):
            self.key_type = key_type.INPUTLESS

    # This will actually run the motion.py command using the parameters determined in the process_key_type() function
    def process_key_command(self):
        if self.key_type == key_type.MOTION:
            self.motion.move_step(self.motor, self.direction)
        elif self.key_type == key_type.SETTER:
            if self.hotkey == "shift + j":
                self.motion.set_jog_step_linear_input()
            elif self.hotkey == "shift + g":
                self.motion.set_jog_step_rotational()
            elif self.hotkey == "shift + k":
                self.motion.set_velocity()
        elif self.key_type == key_type.INPUTLESS:
            if self.hotkey == "space":
                self.motion.stop_all()
            elif self.hotkey == "h":
                self.motion.help_me()
            elif self.hotkey == "o":
                self.motion.home_motors()


# Single Press State Machine
class single_sm:
    def __init__(
        self,
        state: single_states = single_states.INIT,
        count: int = 0,
        motion: motpy.Motion = motpy.Motion.get_instance(),
    ):
        self.state = state
        self.count = count
        self.act = single_action(motion)

    def moore_sm(self):
        if self.state == single_states.INIT:
            self.act.init()
            self.state = single_states.WAIT
        elif self.state == single_states.WAIT:
            self.act.wait()
            if self.act.single_key_pressed():
                self.state = single_states.ADC_FILTER
            else:
                self.state = single_states.WAIT
        elif self.state == single_states.ADC_FILTER:
            if self.count < SINGLE_MAX_ADC_COUNTER:
                self.state = single_states.ADC_FILTER
                self.count += 1
            else:
                self.state = single_states.PRESS
                self.count = 0
        elif self.state == single_states.PRESS:
            self.act.press()
            if self.act.same_key_pressed():
                self.state = single_states.PRESS
            else:
                self.act.release()
                self.state = single_states.WAIT
        else:
            self.state = single_states.INIT
