import autogator.datacache as glob

cache = glob.DataCache.get_instance()

# Distances in mm
sweep_distance = 0.1
step_size = 0.01

cache.get_dataScanner().basic_scan(sweep_distance=sweep_distance, step_size=step_size)