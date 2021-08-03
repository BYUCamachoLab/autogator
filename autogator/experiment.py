import autogator.datacache as glob

class Experiment:
    def __init__(self):
        self.dataCache = glob.DataCache.get_instance()

    def run(self):
        raise NotImplementedError

    def set_filename(self, loc_X, loc_y):
        raise NotImplementedError