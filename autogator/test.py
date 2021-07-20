# from autogator.experiment.datascanner import DataScanner
# from pyrolab.drivers.scopes.rohdeschwarz import RTO
# from motion.motion import Motion

# motion = Motion()
# motion.keyloop()
# scope = RTO("10.32.112.162", protocol="INSTR", timeout=10000)
# scanner = DataScanner(scope, motion, channel=3)

# scanner.auto_scan()
# scope.set_timescale(1e-9)
# scope.set_channel(3, range=.4, coupling="DCLimit", position=0)
# scope.set_auto_measurement(3)
# scope.wait_for_device()
# print(scope.measure())

from autogator.dataCache import DataCache

dataCache = DataCache()

dataCache.get_dataScanner().auto_scan()