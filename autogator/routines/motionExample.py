from packages.motion import *
from packages.map import Map

map = Map("circuits.txt")

calibration_circuits = map.filter("ports", "test")

calibrate(calibration_circuits.circuits)

map = Map("circuits.txt") 

circuits_to_go_to = map.filter_out("ports", "test")

for circuit in circuits_to_go_to.circuits:
    go_to_circuit(circuit)
    print(circuit.name)
    input("Press Enter for next circuit")