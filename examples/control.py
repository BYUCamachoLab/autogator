import autogator.dataCache as dataCache
import autogator.config as cfg

state_machine = dataCache.DataCache.get_instance()
state_machine.load_configuration()
if cfg.coord_config.origin == None:
    print("Origin was not found, Must Recalibrate")
    state_machine.concentric_calibration()
    state_machine.set_configuration()
state_machine.run_sm()