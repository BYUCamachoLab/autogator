import autogator.dataCache

cache = autogator.dataCache.DataCache.get_instance()
cache.load_configuration()
cache.concentric_calibration()
mot = cache.motion.get_instance()
for i in range(9):
    input("Press Enter For Next Rotation: ")
    mot.concentric_rotatation()


for i in range(9):
    input("Press Enter For Next Rotation: ")
    mot.concentric_rotatation("backward")
