from pyrolab.api import locate_ns, Proxy

from autogator.expirement.platform_calibrator import PlatformCalibrator
from pyrolab.drivers.scopes.rohdeschwarz import RTO

ns = locate_ns(host="camacholab.ee.byu.edu")
# lamp = Proxy(ns.lookup("LAMP"))
# lamp.start()
# lamp.on()

scope = RTO("10.32.112.162", protocol="INSTR")
platform = PlatformCalibrator("examples/circuits.txt", scope)

platform.calibrate()
