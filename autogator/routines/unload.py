import autogator.dataCache as dataCache

cache = dataCache.DataCache.get_instance()

if cache.unload_position is None:
    print("Go to unload position then press 'q'")
    cache.motion.keyloop()
    cache.configuration.attrs["unload_position"] = [cache.motion.get_motor_position(cache.motion.x_mot), cache.motion.get_motor_position(cache.motion.y_mot)]
    cache.configuration.save()
    cache.unload_position = cache.configuration.attrs["unload_position"]

cache.motion.go_to_stage_coordinates(cache.unload_position[0], cache.unload_position[1])