from autogator.platformCalibrator.platformCalibrator import PlatformCalibrator
from pyrolab.drivers.scopes.rohdeschwarz import RTO

scope = RTO("10.32.112.162", protocol="INSTR")
platform = PlatformCalibrator("circuits.txt", scope)

platform.calibrate()