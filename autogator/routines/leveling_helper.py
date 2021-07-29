import autogator.dataCache as dataCache
import keyboard
import os

cache = dataCache.DataCache.get_instance()

log_more_points = "y"
go_to_more_points = "y"
stage_points = {}

while log_more_points == "y":
    print("Go to point you want to log, then press 'q'")
    cache.motion.keyloop()
    os.system("cls")
    new_point_key = input("Input the key you want to reference this point: ")
    stage_points[new_point_key] = [cache.motion.get_motor_position(cache.motion.x_mot), cache.motion.get_motor_position(cache.motion.y_mot)]
    log_more_points = input("Log another point? (y,n): ")

flags = {}

def set_flag(flag: str) -> None:
    global flags
    flags[flag] = True

for key in stage_points:
    flags[key] = False
    keyboard.on_press_key(key, lambda _: set_flag(key))

while True:
    if keyboard.is_pressed("q"):
        print("QUIT")
        break
    for flag in flags:
        if flags[flag]:
            cache.motion.go_to_stage_coordinates(stage_points[flag][0], stage_points[flag][1])
            flags[flag] = False
