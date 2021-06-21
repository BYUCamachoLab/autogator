import autogator.dataCache

cache = autogator.dataCache.DataCache.get_instance()
cache.load_configuration()
mot = cache.motion.get_instance()
original_step_size = mot.r_mot.jog_step_size
mot.r_mot.jog_step_size = 10
#for i in range(1):
input("Press Enter For Next Rotation: ")
mot.concentric_rotatation()
input("Press Enter For Next Rotation: ")
mot.concentric_rotatation()


#for i in range(1):
input("Press Enter For Next Rotation: ")
mot.concentric_rotatation("backward")
input("Press Enter For Next Rotation: ")
mot.concentric_rotatation("backward")
mot.r_mot.jog_step_size = original_step_size
