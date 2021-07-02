from autogator.map import Map
from autogator.experiment.sweep_experiment import SweepExperiment

map = Map("circuits_test.txt")
map2 = map.search("MZIs_1 + MZI2")
print(map2)
SweepExperiment(map2.circuits, 1500, 1600, 15, 12)
