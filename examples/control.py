import autogator.dataCache as dataCache

state_machine = dataCache.DataCache.get_instance()
state_machine.run_sm()
