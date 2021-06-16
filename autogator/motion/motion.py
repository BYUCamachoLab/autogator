from ctypes import c_int, c_double, byref, pointer
import numpy as np
import time
import keyboard
import os
import autogator.map.map as map

from pyrolab.api import locate_ns, Proxy
ns = locate_ns(host="camacholab.ee.byu.edu")

help_txt = """\nControls\n--------\n
    \tleft arrow - jog move left
    \tright arrow - jog move right
    \tdown arrow - jog move down
    \tup arrow - jog move up
    \tc - jog clockwise rotation
    \tx - jog counterclockwise rotation
    \ta - continuous move left
    \td - continuous move right
    \ts - continuous move down
    \tw - continuous move up
    \tshift + j - jog step size (linear motors)
    \tshift + g - jog step size (rotational motor)
    \tshift + k - set velocity (mm/s)
    \tspacebar - emergency stop all
    \to - home linear motors
    \th - help
    \tq - quit
    """
NO_CHARACTER_KEYS = [
    'left arrow',
    'right arrow',
    'down arrow',
    'up arrow',
    'shift',
    'ctrl',
    'alt',
    'caps lock'
]

def is_no_char_key(input)->bool:
    str_input = str(input).replace("KeyboardEvent(", "").replace(" down)", "")
    if(str_input.count("up") != 0):
        return True
    output = False
    for key in NO_CHARACTER_KEYS:
        output |= str_input == key
    return output

def clear():
    keystrokes = keyboard.stop_recording()
    count = 0
    for stroke in keystrokes:
        if not is_no_char_key(stroke):
            keyboard.write("\b")
            count += 1
    print("There were a total of " + str(len(keystrokes)) + " keys recorded and "+ str(count) + " deleted")

class Motion:
    __instance = None
    def __init__(self):
        # Singleton Method
        if Motion.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            # Gets the motors
            self.x_mot = Proxy(ns.lookup("KCUBE_LAT"))
            self.y_mot = Proxy(ns.lookup("KCUBE_LON"))
            self.r_mot = Proxy(ns.lookup("KCUBE_ROT"))
            self.motors = [self.x_mot, self.y_mot, self.r_mot]

            self.conversion_matrix = None

            # Sets these to false so that motors can move without intereference
            self.x_mot_moving = False
            self.y_mot_moving = False
            self.r_mot_moving = False

            # key flags, boolean of whether they are pressed
            self.flags = {
                "left_arrow_pressed": False,
                "left_arrow_released": False,
                "right_arrow_pressed": False,
                "right_arrow_released": False,
                "up_arrow_pressed": False,
                "up_arrow_released": False,
                "down_arrow_pressed": False,
                "down_arrow_released": False,
                "c_pressed": False,
                "c_released": False,
                "x_pressed": False,
                "x_released": False,
                "a_pressed": False,
                "a_released": False,
                "d_pressed": False,
                "d_released": False,
                "w_pressed": False,
                "w_released": False,
                "s_pressed": False,
                "s_released": False,
                "space_pressed": False,
                "h_pressed": False,
                "o_pressed": False,
                "shift_j": False,
                "shift_g": False,
                "shift_k": False
            }

            # Set the singleton instance to self
            Motion.__instance = self

    # Grabs the singleton instance of motion
    @staticmethod
    def get_instance():
        # If the object is not instantiated this will instantiate it.
        if Motion.__instance == None:
            Motion()
        return Motion.__instance

    # Stops a continuoss movement
    def stop_cont_jog(self, motor, move_type: str="continuous") -> None:
        # Stops the motor
        if move_type == "continuous":
            motor.stop()
        # Sets the movement boolean to false
        if motor == self.x_mot:
            self.x_mot_moving = False
        if motor == self.y_mot:
            self.y_mot_moving = False
        if motor == self.r_mot:
            self.r_mot_moving = False

    # Doesn't work, but is never used, sets the speed of a continuous movement
    def set_velocity(self):
        #clear()
        os.system('cls')
        velocity = float(input('New velocity (device units):'))
        for m in self.motors:
            m.velocity = velocity
        #keyboard.start_recording()

    # Sets the step size of a step movement
    def set_jog_step_linear_input(self):
        os.system('cls')
        step = float(input('New Jog Step (mm):'))
        self.x_mot.jog_step_size = step
        self.y_mot.jog_step_size = step

    # Sets the step size with a function call
    def set_jog_step_linear(self,step_size):
        self.x_mot.jog_step_size = step_size
        self.y_mot.jog_step_size = step_size

    # Sets the rotational step
    def set_jog_step_rotational(self):
        os.system('cls')
        step = float(input('New Jog Step (degrees):'))
        self.r_mot.jog_step_size = step

    # Stops All Motors, but then requires K Cubes to be restarted
    def stop_all(self):
        for m in self.motors:
            m.stop()

    def move_step(self, motor, direction):
        if motor == self.x_mot:
            if self.x_mot_moving == False:
                motor.jog(direction)
                #x_mot_moving = True
        if motor == self.y_mot:
            if self.y_mot_moving == False:
                motor.jog(direction)
                #y_mot_moving = True
        if motor == self.r_mot:
            if self.r_mot_moving == False:
                motor.jog(direction)
                #r_mot_moving = True

    def move_cont(self,motor, direction):
        if motor == self.x_mot:
            if self.x_mot_moving == False:
                motor.move_continuous(direction)
                self.x_mot_moving = True
        if motor == self.y_mot:
            if self.y_mot_moving == False:
                motor.move_continuous(direction)
                self.y_mot_moving = True
        if motor == self.r_mot:
            if self.r_mot_moving == False:
                motor.move_continuous(direction)
                self.r_mot_moving = True

    # Prints the keys and their function
    def help_me(self) -> None:
        global help_txt
        print(help_txt)

    # Set the flag value true
    def set_flag(self, flag: str) -> None:
        self.flags[flag] = True

    # Set the step size flag to true
    def set_flag_lin_step(self) -> None:
        self.flags["shift_j"] = True  

    # Set the rotation step size flag to true
    def set_flag_rot_step(self) -> None:
        self.flags["shift_g"] = True

    # Set the velocity speed flag to true
    def set_flag_vel(self) -> None:
        self.flags["shift_k"] = True

    def keyloop(self,quitKey = 'q'):
        keyboard.on_press_key('left arrow', lambda _:self.set_flag('left_arrow_pressed'))
        keyboard.on_release_key('left arrow', lambda _:self.set_flag('left_arrow_released'))
        keyboard.on_press_key('right arrow', lambda _:self.set_flag('right_arrow_pressed'))
        keyboard.on_release_key('right arrow', lambda _:self.set_flag('right_arrow_released'))
        keyboard.on_press_key('up arrow', lambda _:self.set_flag('up_arrow_pressed'))
        keyboard.on_release_key('up arrow', lambda _:self.set_flag('up_arrow_released'))
        keyboard.on_press_key('down arrow', lambda _:self.set_flag('down_arrow_pressed'))
        keyboard.on_release_key('down arrow', lambda _:self.set_flag('down_arrow_released'))
        keyboard.on_press_key('c', lambda _:self.set_flag('c_pressed'))
        keyboard.on_release_key('c', lambda _:self.set_flag('c_released'))
        keyboard.on_press_key('x', lambda _:self.set_flag('x_pressed'))
        keyboard.on_release_key('x', lambda _:self.set_flag('x_released'))
        keyboard.on_press_key('a', lambda _:self.set_flag('a_pressed'))
        keyboard.on_release_key('a', lambda _:self.set_flag("a_released"))
        keyboard.on_press_key('d', lambda _:self.set_flag("d_pressed"))
        keyboard.on_release_key('d', lambda _:self.set_flag("d_released"))
        keyboard.on_press_key('w', lambda _:self.set_flag("w_pressed"))
        keyboard.on_release_key('w', lambda _:self.set_flag("w_released"))
        keyboard.on_press_key('s', lambda _:self.set_flag("s_pressed"))
        keyboard.on_release_key('s', lambda _:self.set_flag("s_released"))
        keyboard.add_hotkey('shift + j', self.set_flag_lin_step)
        keyboard.add_hotkey('shift + g', self.set_flag_rot_step)
        keyboard.add_hotkey('shift + k', self.set_flag_vel)        
        keyboard.on_press_key('space', lambda _:self.set_flag("space_pressed"))
        keyboard.on_press_key('h', lambda _:self.set_flag("h_pressed"))
        keyboard.on_press_key('o', lambda _:self.set_flag("o_pressed"))
        #keyboard.on_press_key('d', get_data)

        print(help_txt)

        while True:
            if keyboard.is_pressed(quitKey):
                print("QUIT")
                break
            for flag in self.flags:
                if self.flags[flag]:
                    print(flag)
                    if flag == "left_arrow_pressed":
                        self.move_step(self.x_mot, "backward")
                    elif flag == "left_arrow_released":
                        self.stop_cont_jog(self.x_mot, "step")
                    elif flag == "right_arrow_pressed":
                        self.move_step(self.x_mot, "forward")
                    elif flag == "right_arrow_released":
                        self.stop_cont_jog(self.x_mot, "step")
                    elif flag == "up_arrow_pressed":
                        self.move_step(self.y_mot, "forward")
                    elif flag == "up_arrow_released":
                        self.stop_cont_jog(self.y_mot, "step")
                    elif flag == "down_arrow_pressed":
                        self.move_step(self.y_mot, "backward")
                    elif flag == "down_arrow_released":
                        self.stop_cont_jog(self.y_mot, "step")
                    elif flag == "c_pressed":
                        self.move_step(self.r_mot, "forward")
                    elif flag == "c_released":
                        self.stop_cont_jog(self.r_mot, "step")
                    elif flag == "x_pressed":
                        self.move_step(self.r_mot, "backward")
                    elif flag == "x_released":
                        self.stop_cont_jog(self.r_mot, "step")
                    elif flag == "a_pressed":
                        self.move_cont(self.x_mot, "backward")
                    elif flag == "a_released":
                        self.stop_cont_jog(self.x_mot, "continuous")
                    elif flag == "d_pressed":
                        self.move_cont(self.x_mot, "forward")
                    elif flag == "d_released":
                        self.stop_cont_jog(self.x_mot, "continuous")
                    elif flag == "w_pressed":
                        self.move_cont(self.y_mot, "forward")
                    elif flag == "w_released":
                        self.stop_cont_jog(self.y_mot, "continuous")
                    elif flag == "s_pressed":
                        self.move_cont(self.y_mot, "backward")
                    elif flag == "s_released":
                        self.stop_cont_jog(self.y_mot, "continuous")
                    elif flag == "space_pressed":
                        self.stop_all()
                    elif flag == "h_pressed":
                        self.help_me()
                    elif flag == "o_pressed":
                        self.home_motors()
                    elif flag == "shift_j":
                        self.set_jog_step_linear_input()
                    elif flag == "shift_g":
                        self.set_jog_step_rotational()
                    elif flag == "shift_k":
                        self.set_velocity()
                    
                    self.flags[flag] = False
            
    # Resets the motors to base positions
    def home_motors(self) -> None:
        print("Homing motors...")
        self.x_mot.go_home()
        self.y_mot.go_home()
        print("Done homing")

    # Converts GDS coordinates to chip coordinates and goes to those positions
    def go_to_GDS_Coordinates(self, x: float, y: float) -> None: 
        # The GDS Coordinates
        gds_pos = np.array([[x], 
                            [y], 
                            [1]])

        # In case the conversion matrix has not been set
        if self.conversion_matrix is None:
            raise Exception("Set the conversion Matrix before going to GDS coordinates")
        
        # Calculates the new point and moves to it
        newPoint = self.conversion_matrix @ gds_pos
        self.x_mot.move_to(newPoint[0][0])
        self.y_mot.move_to(newPoint[1][0])
    
    # Will go to GDS y position entered in
    def go_to_GDS_Coordinates_y(self, y_pos: float=None) -> None:
        if y_pos == None:
            y_pos = float(input("Enter in Y Coordinate (mm): "))
        # The GDS Coordinates
        gds_pos = np.array([[self.get_x_position()], 
                            [y_pos], 
                            [1]])

        # In case the conversion matrix has not been set
        if self.conversion_matrix is None:
            raise Exception("Set the conversion Matrix before going to GDS coordinates")
        
        # Calculates the new point and moves to it
        newPoint = self.conversion_matrix @ gds_pos
        self.y_mot.move_to(newPoint[1][0])

    # Will go to GDS x position entered in
    def set_x_position(self, x_pos: float=None) -> None:
        if x_pos == None:
            x_pos = float(input("Enter in X Coordinate (mm): "))
        # The GDS Coordinates
        gds_pos = np.array([[x_pos], 
                            [self.get_y_position()], 
                            [1]])

        # In case the conversion matrix has not been set
        if self.conversion_matrix is None:
            raise Exception("Set the conversion Matrix before going to GDS coordinates")
        
        # Calculates the new point and moves to it
        newPoint = self.conversion_matrix @ gds_pos
        self.x_mot.move_to(newPoint[0][0])

    # Goes to Chip Coordinates, which are more undefined
    def go_to_chip_coordinates(self, x: float, y: float) -> None:
        self.x_mot.move_to(x)
        self.y_mot.move_to(y)

    # Goes to the Chip y coordinate entered in
    def go_to_chip_coordinates_y(self, y: float) -> None:
        self.y_mot.move_to(y)

    # Goes the the Chip x coordinate entered in
    def go_to_chip_coordinates_x(self, x: float) -> None:
        self.x_mot.move_to(x)

    # Goes to the position attributed to the circuit parameter
    def go_to_circuit(self, circuit: map.Circuit) -> None:
        pos = circuit.location
        try:
            self.go_to_GDS_Coordinates(float(pos[0]), float(pos[1]))
        except Exception as e:
            print("Error: Tried to call go_to_GDS_Coordinates()\n" + str(e))

    # Get the y position of the y motor
    def get_y_position(self) -> float:
        return self.y_mot.get_position()

    # Get the x position of motor x
    def get_x_position(self) -> float:
        return self.x_mot.get_position()

    # Get the rotation of the motor r
    def get_r_position(self) -> float:
        return self.r_mot.get_position()

    # Will go to x position entered in
    def set_rotation(self, r_pos: float=None) -> None:
        if r_pos == None:
            r_pos = float(input("Enter in Rotation (deg): "))
        self.r_mot.move_to(r_pos)

    # Set the conversion matrix
    def set_conversion_matrix(self, matrix: np.numarray) -> None:
        self.conversion_matrix = matrix
