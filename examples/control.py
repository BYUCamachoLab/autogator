from autogator.motion import state_machine
from pyrolab.api import locate_ns, Proxy

import autogator.dataCache as dataCache

state_machine = dataCache.DataCache.get_instance()
state_machine.run_sm()