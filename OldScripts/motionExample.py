from autogator.circuitMap import CircuitMap
import autogator.dataCache as data

# Accesses the Data Cache Instance and calibrates
dataCache = data.DataCache.get_instance()
dataCache.calibrate()

# Accesses the Map of Circuits
circuitMap = Map("circuits_test.txt")

circuits_to_go_to = circuitMap.filter_out("ports", "test")

for circuit in circuitMap.circuits:
    dataCache.get_motion().go_to_circuit(circuit)
    print(circuit.ID)
    print(circuit.name)
    input("Press Enter for next circuit")
