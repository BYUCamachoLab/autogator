from autogator.experiment import Experiment
from time import sleep


class FakeExperiment(Experiment):
    def __init__(self):
        super().__init__()
    def run(self):
        print("Running fake eperiment...")
        sleep(5)
        print("Done.")
    def set_filename(self):
        pass