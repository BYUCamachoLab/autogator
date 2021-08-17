from autogator.circuitmap import CircuitMap
from autogator.experiment import WavelengthSweepExperiment, BatchExperiment, FakeExperiment

circuitMap = CircuitMap.loadtxt("C:/Users/mcgeo/source/repos/autogator/development/circuit_files/fabrun5.txt")

testing_circuitMap = circuitMap.filterby(name="MZI2")

testing_experiment = WavelengthSweepExperiment(wl_start=1550, wl_stop=1600, duration=3, sample_rate=100000, power_dBm=14.0)

testBatch = BatchExperiment(circuitMap=testing_circuitMap, experiment=testing_experiment)
testBatch.run()
