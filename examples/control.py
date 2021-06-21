import autogator.dataCache as dataCache

state_machine = dataCache.DataCache.get_instance()
state_machine.load_configuration()
state_machine.run_sm()