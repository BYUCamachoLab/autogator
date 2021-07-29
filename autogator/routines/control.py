"""
Control Routine
-------------------------------------

Runs keyloop function of dataCache to allow motor control.
"""
import autogator.datacache as dataCache

controller = dataCache.DataCache.get_instance()
controller.get_motion().keyloop()
