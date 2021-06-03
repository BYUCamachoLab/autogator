import keyboard
from enum import Enum, auto
#import autogator.motion.motion as motion

#Used for timers in the State Machine
MOTION_MAX_ADC_COUNT = 4 # Debounces Key Presses
MOTION_MAX_CONT_COUNT = 15 # Sets time between movements

# Sets up objects from the motion.py so that actions can be performed
"""
x_motor = motion.x_mot # X axis motor
y_motor = motion.y_mot # Y axis motor
r_motor = motion.r_mot # Rotation motor
"""

motion_hotkeys = [
    'w',
    'a',
    's',
    'd'
]
class motion_states(Enum):
    INIT = auto()
    WAIT = auto()
    CHOICE = auto()
    MOVE = auto()
    ADC_BUFFER = auto()
    ADC_CONT = auto()

class motion_action:
    def __init__(self):
        self.init_printing = False
        self.wait_printing = False
        self.move_type_printing = False
        self.buffer_printing = False
        self.move_printing = False
        self.cont_printing = False
        self.stop_printing = False
        self.key_pressed = None
    
    def init(self):
        self.init_printing = False
        self.wait_printing = False
        self.move_type_printing = False
        self.buffer_printing = False
        self.move_printing = False
        self.cont_printing = False
        self.stop_printing = False
        self.key_pressed = None
        if self.init_printing == False:
            print("Initialized")
            self.init_printing = True

    def wait(self):
        self.init_printing = False
        self.move_type_printing = False
        self.buffer_printing = False
        self.move_printing = False
        self.cont_printing = False
        self.stop_printing = False
        if self.wait_printing == False:
            print("Waiting")
            self.wait_printing = True
    
    def move_type(self):
        self.wait_printing = False
        if self.move_type_printing == False:
            print("Choosing Movement")
            self.move_type_printing = True
    
    def buffer(self):
        self.move_type_printing = False
        self.cont_printing = False
        if self.buffer_printing == False:
            print("ADC Wait Buffer")
            self.buffer_printing = True
   
    def move(self):
        self.move_type_printing = False
        if self.move_printing == False:
            print("Moving " + self.key_pressed)
            self.move_printing = True
    
    def cont(self):
        self.buffer_printing = False
        if self.cont_printing == False:
            print("ADC Continuos Movement " + self.key_pressed)
            self.cont_printing = True
    
    def stop(self):
        self.buffer_printing = False
        self.cont_printing = False
        if self.stop_printing == False:
            print("Stopping")
            self.stop_printing = True
    
    def motion_key_pressed(self):
        output = False
        for hotkey in motion_hotkeys:
            if(keyboard.is_pressed(hotkey)):
                output = True
                self.key_pressed = hotkey
        return output

    def same_key_pressed(self):
        return keyboard.is_pressed(self.key_pressed)

class motion_sm:
    def __init__(self, state: motion_states=motion_states.INIT, count: int=0):
        self.state = state
        self.count = count
        self.act = motion_action()
    
    def moore_sm(self):
        if self.state == motion_states.INIT:
            self.act.init()
            self.state = motion_states.WAIT
        elif self.state == motion_states.WAIT:
            self.act.wait()
            if self.act.motion_key_pressed():
                self.state = motion_states.CHOICE
            else:
                self.state = motion_states.WAIT
        elif self.state == motion_states.CHOICE:
            self.act.move_type()
            if self.act.same_key_pressed():
                if self.count < MOTION_MAX_CONT_COUNT:
                    self.state = motion_states.CHOICE
                    self.count += 1
                else:
                    self.state = motion_states.ADC_BUFFER
                    self.count = 0
            else:
                self.state = motion_states.MOVE
                self.count = 0
        elif self.state == motion_states.MOVE:
            self.act.move()
            self.state = motion_states.WAIT
        elif self.state == motion_states.ADC_BUFFER:
            self.act.buffer()
            if self.act.same_key_pressed():
                if self.count < MOTION_MAX_ADC_COUNT:
                    self.state = motion_states.ADC_BUFFER
                    self.count += 1
                else:
                    self.state = motion_states.ADC_CONT
                    self.count = 0
            else:
                self.act.stop()
                self.state = motion_states.WAIT
                self.count = 0
        elif self.state == motion_states.ADC_CONT:
            self.act.cont()
            if self.act.same_key_pressed():
                self.state = motion_states.ADC_BUFFER
            else:
                self.act.stop()
                self.state = motion_states.WAIT
        else:
            self.state = motion_states.INIT
            self.count = 0