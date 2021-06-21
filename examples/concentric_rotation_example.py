import autogator.dataCache

cache = autogator.dataCache.DataCache.get_instance()
cache.load_configuration()
mot = cache.motion.get_instance()
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
