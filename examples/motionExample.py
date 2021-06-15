import autogator.motion.motion as mot
from autogator.map.map import Map
import autogator.expirement.platformcalibrator as platfrom
import autogator.dataCache as data

dataCache = data.DataCache.get_instance()
oscilliscope = dataCache.get_oscilliscope()
calibrator = platfrom.PlatformCalibrator("circuits_test.txt", oscilliscope)
motion = mot.Motion.get_instance()

calibrator.calibrate()

map = Map("circuits_test.txt") 

circuits_to_go_to = map.filter_out("ports", "test")

for circuit in circuits_to_go_to.circuits:
    motion.go_to_circuit(circuit)
    print(circuit.ID)
    print(circuit.name)
    input("Press Enter for next circuit")