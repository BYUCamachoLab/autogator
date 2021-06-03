import keyboard
from enum import Enum, auto

SINGLE_MAX_ADC_COUNTER = 4
single_hotkeys = [
    'left arrow',
    'right arrow',
    'down arrow',
    'up arrow',
    'c',
    'x',
    'shift + j',
    'shift + g',
    'shift + k',
    'space',
    'o',
    'h'
]
class single_states(Enum):
    INIT = auto()
    WAIT = auto()
    ADC_FILTER = auto()
    PRESS = auto()
    RELEASE = auto()

class single_action:
    def __init__(self):
        self.init_printing = False
        self.wait_printing = False
        self.press_printing = False
        self.release_printing = False
        self.key_pressed = None
    def init(self):
        self.init_printing == False
        self.wait_printing = False
        self.press_printing = False
        self.release_printing = False
        self.key_pressed = None
        if self.init_printing == False:
            print("Initialized")
            self.init_printing = True
    def wait(self):
        self.init_printing = False
        self.release_printing = False
        if self.wait_printing == False:
            print("Waiting")
            self.wait_printing = True
    def press(self):
        self.wait_printing = False
        if self.press_printing == False:
            print("Pressing " + self.key_pressed)
            self.press_printing = True
    def release(self):
        self.press_printing = False
        if self.release_printing == False:
            print("Releasing " + self.key_pressed)
            self.release_printing = True
    
    def single_key_pressed(self):
        output = False
        for hotkey in single_hotkeys:
            if(keyboard.is_pressed(hotkey)):
                output = True
                self.key_pressed = hotkey
        return output
    
    def same_key_pressed(self):
        return keyboard.is_pressed(self.key_pressed)
    
class single_sm():
    def __init__(self, state: single_states=single_states.INIT, count: int=0):
        self.state = state
        self.count = count
        self.act = single_action()

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