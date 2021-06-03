from pyrolab.api import locate_ns, Proxy

from autogator.expirement.platformcalibrator import PlatformCalibrator
from pyrolab.drivers.scopes.rohdeschwarz import RTO
from autogator.motion import motion

ns = locate_ns(host="camacholab.ee.byu.edu")

motion1=motion.Motion()


motion1.keyloop()