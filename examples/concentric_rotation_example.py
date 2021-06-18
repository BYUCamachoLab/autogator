import autogator.dataCache

cache = autogator.dataCache.DataCache.get_instance()
cache.calibrate()
cache.concentric_calibration()
mot = cache.motion.get_instance()
for i in range(90):
    mot.concentric_rotatation()

for i in range(90):
    mot.concentric_rotatation("backward")
