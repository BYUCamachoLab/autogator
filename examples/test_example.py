from autogator.testbatch import TestBatch
from autogator.circuitmap import CircuitMap
from autogator.ws_experiment import WavelengthSweepExperiment
from autogator.fake_experiment import FakeExperiment

circuitMap = CircuitMap("C:\\Users\\mcgeo\\source\\repos\\autogator\\autogator\\circuit_files\\fabrun5.txt")

testing_circuitMap = circuitMap.filter(name="MZI2", grouping=3)

testing_experiment = WavelengthSweepExperiment(wl_start=1550, wl_stop=1600, duration=5.0)
#testing_experiment = FakeExperiment()

testBatch = TestBatch(circuitMap=testing_circuitMap, experiment=testing_experiment)
testBatch.run()