from ctypes import c_int, c_double, byref, pointer
import numpy as np
import time
import keyboard

from pyrolab.drivers.motion.z825b import Z825B
from pyrolab.drivers.motion.prm1z8 import PRM1Z8

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

x_mot = Z825B("27504851", home=False)
y_mot = Z825B("27003497", home=False)
r_mot = PRM1Z8("27003366", home=False)
motors = [x_mot, y_mot, r_mot]

conversion_matrix = np.array([[1]])

point1 = [0,0]
point2 = [0,0]
point3 = [0,0]

x_mot_moving = False
y_mot_moving = False
r_mot_moving = False

def stop_cont_jog(motor, move_type):
    if move_type == "continuous":
        motor.stop()
    if motor == x_mot:
        global x_mot_moving
        x_mot_moving = False
    if motor == y_mot:
        global y_mot_moving
        y_mot_moving = False
    if motor == r_mot:
        global r_mot_moving
        r_mot_moving = False

def set_velocity():
    velocity = float(input('New velocity (device units):'))
    for m in motors:
        m.velocity = velocity

def set_jog_step_linear_input():
    step = float(input('New Jog Step (mm):'))
    x_mot.jog_step_size = step
    y_mot.jog_step_size = step

def set_jog_step_linear(step_size):
    x_mot.jog_step_size = step_size
    y_mot.jog_step_size = step_size
    
def set_jog_step_rotational():
    step = float(input('New Jog Step (degrees):'))
    r_mot.jog_step_size = step

def stop_all():
    for m in motors:
        m.stop()

def move_step(motor, direction):
    if motor == x_mot:
        global x_mot_moving
        if x_mot_moving == False:
            motor.jog(direction)
            #x_mot_moving = True
    if motor == y_mot:
        global y_mot_moving
        if y_mot_moving == False:
            motor.jog(direction)
            #y_mot_moving = True
    if motor == r_mot:
        global r_mot_moving
        if r_mot_moving == False:
            motor.jog(direction)
            #r_mot_moving = True

def move_cont(motor, direction):
    if motor == x_mot:
        global x_mot_moving
        if x_mot_moving == False:
            motor.move_continuous(direction)
            x_mot_moving = True
    if motor == y_mot:
        global y_mot_moving
        if y_mot_moving == False:
            motor.move_continuous(direction)
            y_mot_moving = True
    if motor == r_mot:
        global r_mot_moving
        if r_mot_moving == False:
            motor.move_continuous(direction)
            r_mot_moving = True

def help_me():
    global help_txt
    print(help_txt)

def set_point_1():
    global point1, dataScanner
    point1 = [x_mot.get_position(), y_mot.get_position()]
    print("Point 1 set to (" + str(point1[0]) + "," + str(point1[1]) + ")")

def set_point_2():
    global point2
    point2 = [x_mot.get_position(), y_mot.get_position()]
    print("Point 2 set to (" + str(point2[0]) + "," + str(point2[1]) + ")")

def set_point_3():
    global point3
    point3 = [x_mot.get_position(), y_mot.get_position()]
    print("Point 3 set to (" + str(point3[0]) + "," + str(point3[1]) + ")")

def keyloop_for_calibration():
    keyboard.on_press_key('left arrow', lambda _:move_step(x_mot, "backward"))
    keyboard.on_release_key('left arrow', lambda _:stop_cont_jog(x_mot, "step"))
    keyboard.on_press_key('right arrow', lambda _:move_step(x_mot, "forward"))
    keyboard.on_release_key('right arrow', lambda _:stop_cont_jog(x_mot, "step"))
    keyboard.on_press_key('up arrow', lambda _:move_step(y_mot, "forward"))
    keyboard.on_release_key('up arrow', lambda _:stop_cont_jog(y_mot, "step"))
    keyboard.on_press_key('down arrow', lambda _:move_step(y_mot, "backward"))
    keyboard.on_release_key('down arrow', lambda _:stop_cont_jog(y_mot, "step"))
    keyboard.on_press_key('a', lambda _:move_cont(x_mot, "backward"))
    keyboard.on_release_key('a', lambda _:stop_cont_jog(x_mot, "continuous"))
    keyboard.on_press_key('d', lambda _:move_cont(x_mot, "forward"))
    keyboard.on_release_key('d', lambda _:stop_cont_jog(x_mot, "continuous"))
    keyboard.on_press_key('w', lambda _:move_cont(y_mot, "forward"))
    keyboard.on_release_key('w', lambda _:stop_cont_jog(y_mot, "continuous"))
    keyboard.on_press_key('s', lambda _:move_cont(y_mot, "backward"))
    keyboard.on_release_key('s', lambda _:stop_cont_jog(y_mot, "continuous"))
    keyboard.add_hotkey('shift + j', set_jog_step_linear_input)
    keyboard.add_hotkey('shift + g', set_jog_step_rotational)
    keyboard.add_hotkey('shift + k', set_velocity)
    keyboard.on_press_key('space', lambda _:stop_all())
    keyboard.on_press_key('h', lambda _:help_me())
    keyboard.on_press_key('o', lambda _:home_motors())
    keyboard.add_hotkey('shift + 1', set_point_1)
    keyboard.add_hotkey('shift + 2', set_point_2)
    keyboard.add_hotkey('shift + 3', set_point_3)



    print(help_txt)

    while True:
        if keyboard.is_pressed('q'):
            print("QUIT")
            break

def keyloop(quitKey = 'q'):

    keyboard.on_press_key('left arrow', lambda _:move_step(x_mot, "backward"))
    keyboard.on_release_key('left arrow', lambda _:stop_cont_jog(x_mot, "step"))
    keyboard.on_press_key('right arrow', lambda _:move_step(x_mot, "forward"))
    keyboard.on_release_key('right arrow', lambda _:stop_cont_jog(x_mot, "step"))
    keyboard.on_press_key('up arrow', lambda _:move_step(y_mot, "forward"))
    keyboard.on_release_key('up arrow', lambda _:stop_cont_jog(y_mot, "step"))
    keyboard.on_press_key('down arrow', lambda _:move_step(y_mot, "backward"))
    keyboard.on_release_key('down arrow', lambda _:stop_cont_jog(y_mot, "step"))
    keyboard.on_press_key('c', lambda _:move_step(r_mot, "forward"))
    keyboard.on_release_key('c', lambda _:stop_cont_jog(r_mot, "step"))
    keyboard.on_press_key('x', lambda _:move_step(r_mot, "backward"))
    keyboard.on_release_key('x', lambda _:stop_cont_jog(r_mot, "step"))
    keyboard.on_press_key('a', lambda _:move_cont(x_mot, "backward"))
    keyboard.on_release_key('a', lambda _:stop_cont_jog(x_mot, "continuous"))
    keyboard.on_press_key('d', lambda _:move_cont(x_mot, "forward"))
    keyboard.on_release_key('d', lambda _:stop_cont_jog(x_mot, "continuous"))
    keyboard.on_press_key('w', lambda _:move_cont(y_mot, "forward"))
    keyboard.on_release_key('w', lambda _:stop_cont_jog(y_mot, "continuous"))
    keyboard.on_press_key('s', lambda _:move_cont(y_mot, "backward"))
    keyboard.on_release_key('s', lambda _:stop_cont_jog(y_mot, "continuous"))
    keyboard.add_hotkey('shift + j', set_jog_step_linear_input)
    keyboard.add_hotkey('shift + g', set_jog_step_rotational)
    keyboard.add_hotkey('shift + k', set_velocity)
    keyboard.on_press_key('space', lambda _:stop_all())
    keyboard.on_press_key('h', lambda _:help_me())
    keyboard.on_press_key('o', lambda _:home_motors())
    #keyboard.on_press_key('d', get_data)

    print(help_txt)

    while True:
        if keyboard.is_pressed(quitKey):
            print("QUIT")
            break

def home_motors():
    print("Homing motors...")
    x_mot.go_home()
    y_mot.go_home()
    print("Done homing")

def go_to_GDS_Coordinates(x, y, conversion_matrix): 
    oldPoint = np.array([[x], [y], [1]])
    newPoint = conversion_matrix @ oldPoint
    x_mot.move_to(newPoint[0][0])
    y_mot.move_to(newPoint[1][0])

def go_to_chip_coordinates(x, y):
    x_mot.move_to(x)
    y_mot.move_to(y)

def go_to_chip_coordinates_y(y):
    y_mot.move_to(y)

def go_to_chip_coordinates_x(x):
    x_mot.move_to(x)

def go_to_circuit(circuit):
    pos = circuit.location
    go_to_GDS_Coordinates(float(pos[0]), float(pos[1]))

def calibrate(circuits):
    global point1, point2, point3, conversion_matrix
    home_motors()
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
    print(point1)
    print(point2)
    print(point3)

    GDS = np.array([[float(location1[0]), float(location1[1]), 1, 0, 0, 0], [0, 0, 0, float(location1[0]), float(location1[1]), 1], [float(location2[0]), float(location2[1]), 1, 0, 0, 0], [0, 0, 0, float(location2[0]), float(location2[1]), 1], [float(location3[0]), float(location3[1]), 1, 0, 0, 0], [0, 0, 0, float(location3[0]), float(location3[1]), 1]])

    CHIP = np.array([[point1[0]],[point1[1]],[point2[0]],[point2[1]],[point3[0]],[point3[1]]])

    a = np.linalg.inv(GDS) @ CHIP

    conversion_matrix = np.array([[a[0][0], a[1][0], a[2][0]], [a[3][0], a[4][0], a[5][0]], [0, 0, 1]])

def move_right():
    move_step(x_mot, 'forward')

def move_left():
    move_step(x_mot, 'backward')

def move_up():
    move_step(y_mot, 'forward')

def move_down():
    move_step(y_mot, 'backward')

def get_y_position():
    return y_mot.get_position()

def get_x_position():
    return x_mot.get_position()