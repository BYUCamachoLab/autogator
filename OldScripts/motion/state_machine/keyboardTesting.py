import keyboard
import time
import autogator.motion.state_machine.motionSM as msm
import autogator.motion.state_machine.singleSM as ssm
import autogator.motion.motion as motpy

NO_CHARACTER_KEYS = [
    "left arrow",
    "right arrow",
    "down arrow",
    "up arrow",
    "shift",
    "ctrl",
    "alt",
    "caps lock",
]


def is_no_char_key(input) -> bool:
    str_input = str(input).replace("KeyboardEvent(", "").replace(" down)", "")
    if str_input.count("up") != 0:
        return True
    output = False
    for key in NO_CHARACTER_KEYS:
        output |= str_input == key
    return output


def clear():
    keystrokes = keyboard.stop_recording()
    keyboard.start_recording()
    count = 0
    for stroke in keystrokes:
        if not is_no_char_key(stroke):
            keyboard.write("\b")
            count += 1
    print(
        "There were a total of "
        + str(len(keystrokes))
        + " keys recorded and "
        + str(count)
        + " deleted"
    )


def run(mot: motpy.Motion = motpy.Motion.get_instance()):
    motion_sm = msm.motion_sm(motion=mot)
    single_sm = ssm.single_sm(motion=mot)
    ot = time.time()
    done = False
    # keyboard.start_recording()
    while not done:
        timer = time.time() - ot
        if timer >= 0.01:
            if keyboard.is_pressed("q"):
                done = True
            else:
                motion_sm.moore_sm()
                single_sm.moore_sm()
                ot = time.time()
    # clear()
    # keyboard.stop_recording()
