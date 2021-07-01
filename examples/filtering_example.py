from autogator.map import Map

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

map2 = map.search(circuit_types[1] + " + jogs_0 - grouping_6 - grouping_2")
print(map2)
print()
# print(map.simple_search(circuit_types[1]))
