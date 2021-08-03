import autogator.datacache as dataCache

cache = dataCache.DataCache.get_instance()

if cache.load_position is None:
    print("Go to load position then press 'q'")
    cache.motion.keyloop()
    cache.configuration.attrs["load_position"] = [cache.motion.get_motor_position(cache.motion.x_mot), cache.motion.get_motor_position(cache.motion.y_mot)]
    cache.configuration.save() 
    cache.load_position = cache.configuration.attrs["load_position"]

cache.motion.go_to_stage_coordinates(cache.load_position[0], cache.load_position[1])