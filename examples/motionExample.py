import autogator.motion.motion as mot
from autogator.map.map import Map
import autogator.expirement.platformcalibrator as platfrom
import autogator.global_objects as glob

calibrator = platfrom.PlatformCalibrator("circuits_test.txt", glob.globals_obj.get_oscilliscope())
motion = mot.Motion()

calibrator.calibrate()

map = Map("circuits_test.txt") 

circuits_to_go_to = map.filter_out("ports", "test")

for circuit in circuits_to_go_to.circuits:
    motion.go_to_circuit(circuit)
    print(circuit.id)
    print(circuit.name)
    input("Press Enter for next circuit")