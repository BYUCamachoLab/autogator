import autogator.datacache as glob

class Experiment:
    def __init__(self):
        self.dataCache = glob.DataCache.get_instance()

    def run(self):
        raise NotImplementedError
