class Experiment:
    def __init__(self, registry):
        self.instruments = registry.get_instruments()
​
    def run(self):
        raise NotImplementedError