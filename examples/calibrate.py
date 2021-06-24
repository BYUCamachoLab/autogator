import autogator.data_cache as cache

cal = cache.DataCache.get_instance()
cal.calibrate()
cal.set_configuration()
