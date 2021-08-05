import autogator.datacache as dataCache

cache = dataCache.DataCache.get_instance()

cache.get_dataScanner().auto_scan(channel=1)