from autogator.datacache import DataCache
import sys

dataCache = DataCache()

class TestBatch:
    def __init__(self, circuitMap, experiment):
        self.circuitMap = circuitMap
        self.experiment = experiment
    
    def run(self):
        # need_to_calibrate = input("Does the stage need to be calibrated? (y,n): ")
        # if need_to_calibrate == "y":
        #     dataCache.calibrate()
        
        test_circuits = self.circuitMap.get_circuits()

        print("Starting testing...")
        for circuit in test_circuits:
            print("Testing: " + str(circuit.ID))
            dataCache.get_motion().go_to_circuit(circuit)
            self.experiment.set_filename("fabrun5", circuit.location[0], circuit.location[1])
            # dataCache.get_dataScanner().auto_scan()
            self.experiment.run()
        print("Done testbatch")
        