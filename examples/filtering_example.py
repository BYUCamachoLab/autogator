from autogator.map import Map
from autogator.experiment.sweep_experiment import SweepExperiment

circuit_types = [
    "DC_top",
    "DIOH_dc",
    "MZIs",
    "RR_top",
    "SIOH_bdc",
    "SIOH_dc",
    "circuit",
    "filters",
    "gen2",
]

map = Map("circuits_test.txt")

map2 = map.search("MZIs_1 + MZI2")
print(map2)
print()
SweepExperiment(map2.circuits, 1500, 1600, 15, 12)

