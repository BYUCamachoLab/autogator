"""
Calibrate Routine
-------------------------------------

Runs calibrate function of dataCache in order to find new conversion matrix.
"""
import autogator.dataCache as dataCache

cal = dataCache.DataCache.get_instance()
cal.calibrate()