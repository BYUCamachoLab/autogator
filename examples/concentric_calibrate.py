import autogator.data_cache as data_cache

cache = data_cache.DataCache.get_instance()
cache.load_configuration()
cache.concentric_calibration()
cache.set_configuration()
