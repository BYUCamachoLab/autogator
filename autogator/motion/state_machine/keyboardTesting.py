import keyboard
import time
import autogator.motion.state_machine.motionSM as msm
import autogator.motion.state_machine.singleSM as ssm

def run():
    motion_sm = msm.motion_sm()
    single_sm = ssm.single_sm()
    ot = time.time()
    done = False
    while not done:
        timer = time.time() - ot
        if(timer >= .01):
            if keyboard.is_pressed('q'):
                done = True
            else:
                motion_sm.moore_sm()
                single_sm.moore_sm()
                ot = time.time()