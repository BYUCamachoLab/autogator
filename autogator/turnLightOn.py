### Steps to turn lamp on remotely
from Pyro5.api import locate_ns
from Pyro5.api import Proxy
ns = locate_ns(host="camacholab.ee.byu.edu")
lamp = Proxy(ns.lookup("LAMP"))
lamp.start()
lamp.on()