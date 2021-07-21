### Steps to turn lamp on remotely
from Pyro5.api import locate_ns
from Pyro5.api import Proxy
import time

ns = locate_ns
ns = locate_ns(host="camacholab.ee.byu.edu")
lamp = Proxy(ns.lookup("LAMP"))
lamp.start()
time.sleep(5)
lamp.on()
