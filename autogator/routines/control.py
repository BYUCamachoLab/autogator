import autogator.dataCache as dataCache

controller = dataCache.DataCache.get_instance()
controller.get_motion().keyloop()