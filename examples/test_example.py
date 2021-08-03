from autogator.testbatch import TestBatch
from autogator.circuitmap import CircuitMap
from autogator.ws_experiment import WavelengthSweepExperiment
from autogator.fake_experiment import FakeExperiment

circuitMap = CircuitMap("C:/Users/camacho/autogator/autogator/circuit_files/fabrun5.txt")

testing_circuitMap = circuitMap.filter(ID="grouping_3::gen2_1::opt_hybrid_jogs_1_1")

testing_experiment = WavelengthSweepExperiment(wl_start=1550, wl_stop=1600, duration=5.0, sample_rate=1, power_dBm=14.0)
#testing_experiment = FakeExperiment()

testBatch = TestBatch(circuitMap=testing_circuitMap, experiment=testing_experiment)
testBatch.run()