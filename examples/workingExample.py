import autogator
from pyrolab.drivers.scopes.rohdeschwarz import RTO

scope = RTO("10.32.112.162", protocol="INSTR")

platformcalib = autogator.expirement.PlatformCalibrator("examples/circuits.txt", scope)

platformcalib.calibrate()