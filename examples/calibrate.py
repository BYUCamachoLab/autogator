import autogator.dataCache as dataCache

cal = dataCache.DataCache.get_instance()
cal.calibrate()
cal.set_configuration()