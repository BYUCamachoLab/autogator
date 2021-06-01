from ctypes import c_int, c_double, byref, pointer
import numpy as np
import time
import keyboard

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
class Motion():
    def __init__(self):
        self.x_mot = Proxy(ns.lookup("KCUBE_LAT"))
        self.y_mot = Proxy(ns.lookup("KCUBE_LON"))
        self.r_mot = Proxy(ns.lookup("KCUBE_ROT"))
        self.motors = [self.x_mot, self.y_mot, self.r_mot]

        self.conversion_matrix = np.array([[1]])

        self.point1 = [0,0]
        self.point2 = [0,0]
        self.point3 = [0,0]

        self.x_mot_moving = False
        self.y_mot_moving = False
        self.r_mot_moving = False

        # keyboard flags
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

    def stop_cont_jog(self, motor, move_type):
        if move_type == "continuous":
            motor.stop()
        if motor == self.x_mot:
            self.x_mot_moving = False
        if motor == self.y_mot:
            self.y_mot_moving = False
        if motor == self.r_mot:
            self.r_mot_moving = False

    def set_velocity(self):
        velocity = float(input('New velocity (device units):'))
        for m in self.motors:
            m.velocity = velocity

    def set_jog_step_linear_input(self):
        step = float(input('New Jog Step (mm):'))
        self.x_mot.jog_step_size = step
        self.y_mot.jog_step_size = step

    def set_jog_step_linear(self,step_size):
        self.x_mot.jog_step_size = step_size
        self.y_mot.jog_step_size = step_size
        
    def set_jog_step_rotational(self):
        step = float(input('New Jog Step (degrees):'))
        self.r_mot.jog_step_size = step

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

    def help_me(self):
        global help_txt
        print(help_txt)

    def set_point_1(self):
        self.point1 = [self.x_mot.get_position(), self.y_mot.get_position()]
        print("Point 1 set to (" + str(self.point1[0]) + "," + str(self.point1[1]) + ")")

    def set_point_2(self):
        self.point2 = [self.x_mot.get_position(), self.y_mot.get_position()]
        print("Point 2 set to (" + str(self.point2[0]) + "," + str(self.point2[1]) + ")")

    def set_point_3(self):
        self.point3 = [self.x_mot.get_position(), self.y_mot.get_position()]
        print("Point 3 set to (" + str(self.point3[0]) + "," + str(self.point3[1]) + ")")

    def keyloop_for_calibration(self):
        keyboard.on_press_key('left arrow', lambda _:self.move_step(self.x_mot, "backward"))
        keyboard.on_release_key('left arrow', lambda _:self.stop_cont_jog(self.x_mot, "step"))
        keyboard.on_press_key('right arrow', lambda _:self.move_step(self.x_mot, "forward"))
        keyboard.on_release_key('right arrow', lambda _:self.stop_cont_jog(self.x_mot, "step"))
        keyboard.on_press_key('up arrow', lambda _:self.move_step(self.y_mot, "forward"))
        keyboard.on_release_key('up arrow', lambda _:self.stop_cont_jog(self.y_mot, "step"))
        keyboard.on_press_key('down arrow', lambda _:self.move_step(self.y_mot, "backward"))
        keyboard.on_release_key('down arrow', lambda _:self.stop_cont_jog(self.y_mot, "step"))
        keyboard.on_press_key('a', lambda _:self.move_cont(self.x_mot, "backward"))
        keyboard.on_release_key('a', lambda _:self.stop_cont_jog(self.x_mot, "continuous"))
        keyboard.on_press_key('d', lambda _:self.move_cont(self.x_mot, "forward"))
        keyboard.on_release_key('d', lambda _:self.stop_cont_jog(self.x_mot, "continuous"))
        keyboard.on_press_key('w', lambda _:self.move_cont(self.y_mot, "forward"))
        keyboard.on_release_key('w', lambda _:self.stop_cont_jog(self.y_mot, "continuous"))
        keyboard.on_press_key('s', lambda _:self.move_cont(self.y_mot, "backward"))
        keyboard.on_release_key('s', lambda _:self.stop_cont_jog(self.y_mot, "continuous"))
        keyboard.add_hotkey('shift + j', self.set_jog_step_linear_input)
        keyboard.add_hotkey('shift + g', self.set_jog_step_rotational)
        keyboard.add_hotkey('shift + k', self.set_velocity)
        keyboard.on_press_key('space', lambda _:self.stop_all())
        keyboard.on_press_key('h', lambda _:self.help_me())
        keyboard.on_press_key('o', lambda _:self.home_motors())
        keyboard.add_hotkey('shift + 1', self.set_point_1)
        keyboard.add_hotkey('shift + 2', self.set_point_2)
        keyboard.add_hotkey('shift + 3', self.set_point_3)



        print(help_txt)

        while True:
            if keyboard.is_pressed('q'):
                print("QUIT")
                break

    def set_flag(self, flag):
        self.flags[flag] = True

    def set_flag_lin_step(self):
        self.flags["shift_j"] = True  

    def set_flag_rot_step(self):
        self.flags["shift_g"] = True

    def set_flag_vel(self):
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
            

    def home_motors(self):
        print("Homing motors...")
        self.x_mot.go_home()
        self.y_mot.go_home()
        print("Done homing")

    def go_to_GDS_Coordinates(self,x, y): 
        oldPoint = np.array([[x], [y], [1]])
        newPoint = self.conversion_matrix @ oldPoint
        self.x_mot.move_to(newPoint[0][0])
        self.y_mot.move_to(newPoint[1][0])

    def go_to_chip_coordinates(self,x, y):
        self.x_mot.move_to(x)
        self.y_mot.move_to(y)

    def go_to_chip_coordinates_y(self,y):
        self.y_mot.move_to(y)

    def go_to_chip_coordinates_x(self,x):
        self.x_mot.move_to(x)

    def go_to_circuit(self,circuit):
        pos = circuit.location
        go_to_GDS_Coordinates(float(pos[0]), float(pos[1]))

    def calibrate(self,circuits):
        # self.home_motors()
        print("Starting calibration process...")
        print("Move " + circuits[0].name + " into Crosshairs, then press shift + 1")
        print("Then Move " + circuits[1].name + " into Crosshairs, then press shift + 2")
        print("Then Move " + circuits[2].name + " into Crosshairs, then press shift + 3")
        keyloop_for_calibration()
        location1 = circuits[0].location
        location2 = circuits[1].location
        location3 = circuits[2].location
        print("GDS locations:")
        print(location1)
        print(location2)
        print(location3)
        print("Chip locations:")
        print(self.point1)
        print(self.point2)
        print(self.point3)

        GDS = np.array([[float(location1[0]), float(location1[1]), 1, 0, 0, 0], [0, 0, 0, float(location1[0]), float(location1[1]), 1], [float(location2[0]), float(location2[1]), 1, 0, 0, 0], [0, 0, 0, float(location2[0]), float(location2[1]), 1], [float(location3[0]), float(location3[1]), 1, 0, 0, 0], [0, 0, 0, float(location3[0]), float(location3[1]), 1]])

        CHIP = np.array([[self.point1[0]],[self.point1[1]],[self.point2[0]],[self.point2[1]],[self.point3[0]],[self.point3[1]]])

        a = np.linalg.inv(GDS) @ CHIP

        self.conversion_matrix = np.array([[a[0][0], a[1][0], a[2][0]], [a[3][0], a[4][0], a[5][0]], [0, 0, 1]])

    def move_right(self):
        move_step(self.x_mot, 'forward')

    def move_left(self):
        move_step(self.x_mot, 'backward')

    def move_up(self):
        move_step(self.y_mot, 'forward')

    def move_down(self):
        move_step(self.y_mot, 'backward')

    def get_y_position(self):
        return self.y_mot.get_position()

    def get_x_position(self):
        return self.x_mot.get_position()