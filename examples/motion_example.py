from autogator.map.map import Map
import autogator.dataCache as data

# Accesses the Data Cache Instance and calibrates
dataCache = data.DataCache.get_instance()
dataCache.load_configuration()

# Accesses the Map of Circuits
map = Map("circuits_test.txt")

circuits_to_go_to = map.filter_out("ports", "test")

for circuit in map.circuits:
    dataCache.get_motion().go_to_circuit(circuit)
    print(circuit.ID)
    print(circuit.name)
    input("Press Enter for next circuit")
