import autogator.datacache as glob

cache = glob.DataCache.get_instance()

# Distances in mm
sweep_distance_x = 0.5
step_size_x = 0.05
sweep_distance_y = 0.1
step_size_y = 0.01

cache.get_dataScanner().basic_scan_rect(sweep_distance_x=sweep_distance_x, sweep_distance_y=sweep_distance_y, step_size_x=step_size_x, step_size_y=step_size_y, plot=True)