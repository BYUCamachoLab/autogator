from autogator.experiment import Experiment
import time


class FakeExperiment(Experiment):
    def __init__(self):
        super().__init__()
    def run(self):
        print("Running fake eperiment...")
        sleep(5)
        print("Done.")