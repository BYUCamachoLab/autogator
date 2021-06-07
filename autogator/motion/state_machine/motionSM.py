import keyboard
from enum import Enum, auto
import autogator.motion.motion as motpy

#Used for timers in the State Machine
MOTION_MAX_ADC_COUNT = 4 # Debounces Key Presses
MOTION_MAX_CONT_COUNT = 15 # Sets time between movements

# keys pressed that use this state machine
motion_hotkeys = [
    'w',
    'a',
    's',
    'd'
]

# States in the state machine
class motion_states(Enum):
    INIT = auto()
    WAIT = auto()
    CHOICE = auto()
    MOVE = auto()
    ADC_BUFFER = auto()
    ADC_CONT = auto()

# A class that will perform tasks outside of the state machine to enhance readability
class motion_action:
    def __init__(self, motion):
        self.init_printing = False
        self.wait_printing = False
        self.move_type_printing = False
        self.buffer_printing = False
        self.move_printing = False
        self.cont_printing = False
        self.stop_printing = False
        self.hotkey = None
        self.motor = None
        self.direction = None
        self.motion = motion
    
    # Initializes the motion object
    def init(self):
        self.init_printing = False
        self.wait_printing = False
        self.move_type_printing = False
        self.buffer_printing = False
        self.move_printing = False
        self.cont_printing = False
        self.stop_printing = False
        self.hotkey = None
        self.motor = None
        self.direction = None
        if self.init_printing == False:
            print("Initialized")
            self.init_printing = True

    # Waits for a key press
    def wait(self):
        self.init_printing = False
        self.move_type_printing = False
        self.buffer_printing = False
        self.move_printing = False
        self.cont_printing = False
        self.stop_printing = False
        self.hotkey = None
        self.motor = None
        self.direction = None
        if self.wait_printing == False:
            print("Waiting")
            self.wait_printing = True
    
    # The SM is choosing between a step and a jog and grabs the direction and motor
    def move_type(self):
        self.wait_printing = False
        if self.move_type_printing == False:
            print("Choosing Movement")
            self.motor, self.direction = self.process_key(self.hotkey)
            self.move_type_printing = True
    
    # Buffer so it stalls a continuous movement
    def buffer(self):
        self.move_type_printing = False
        self.cont_printing = False
        if self.buffer_printing == False:
            print("ADC Wait Buffer")
            self.buffer_printing = True
    
    # A Single Step Movement
    def move(self):
        self.move_type_printing = False
        if self.move_printing == False:
            print("Moving " + self.hotkey)
            self.motion.move_step(self.motor, self.direction)
            self.move_printing = True
    
    # A continuous movement will be performed
    def cont(self):
        self.buffer_printing = False
        if self.cont_printing == False:
            print("ADC Continuos Movement " + self.hotkey)
            self.motion.move_cont(self.motor, self.direction)
            self.cont_printing = True
    
    # Stops the movement
    def stop(self):
        self.buffer_printing = False
        self.cont_printing = False
        if self.stop_printing == False:
            print("Stopping")
            self.motion.stop_cont_jog(self.motor, "continuous")
            self.stop_printing = True
    # This will process the key pressed and return values corresponding to the pressed key
    def process_key(self, hotkey: str):
        if hotkey == 'w':
            return self.motion.y_motor, "forward"
        elif hotkey == 'a':
            return self.motion.x_motor, "backward"
        elif hotkey == 's':
            return self.motion.y_motor, "backward"
        elif hotkey == 'd':
            return self.motion.x_motor, "forward"
    # Gets the key pressed and returns true if any key was pressed
    def motion_key_pressed(self) -> bool:
        output = False
        for hotkey in motion_hotkeys:
            if(keyboard.is_pressed(hotkey)):
                output = True
                self.hotkey = hotkey
        return output

    # Determines if the same key is being pressed
    def same_key_pressed(self) -> bool:
        return keyboard.is_pressed(self.hotkey)

class motion_sm:
    def __init__(self, state: motion_states=motion_states.INIT, count: int=0, motion: motpy.Motion=motpy.Motion()):
        self.state = state
        self.cont_active = False
        self.count = count
        self.act = motion_action(motion)
    
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
                    self.cont_active = True
                    self.count = 0
            else:
                if self.cont_active: 
                    self.act.stop()
                    self.cont_active = False
                self.state = motion_states.WAIT
                self.count = 0
        elif self.state == motion_states.ADC_CONT:
            self.act.cont()
            if self.act.same_key_pressed():
                self.state = motion_states.ADC_BUFFER
            else:
                self.act.stop()
                self.cont_active = False
                self.state = motion_states.WAIT
        else:
            self.state = motion_states.INIT
            self.count = 0
