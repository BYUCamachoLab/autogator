from json import load

from matplotlib.pyplot import autoscale
from autogator.api import load_default_configuration
from autogator.circuit import CircuitMap
from autogator.routines import KeyboardControl, KeyloopKeyboardBindings, auto_scan, basic_scan, calibrate, easy_switcher


def scope_configure_single_meas():
    oscope = stage.scope.driver

    # Scope setup
    CHANNEL = 1
    RANGE = 0.6
    COUPLING = "DCLimit"
    POSITION = -2.0

    oscope.set_channel(CHANNEL, range=RANGE, coupling=COUPLING, position=POSITION)
    oscope.set_auto_measurement(source=F"C{CHANNEL}W1")
    oscope.wait_for_device()


def laser_configure():
    laser = stage.laser
    laser.on()
    laser.power(-4.0)
    laser.wavelength(1550.0)


def keyboard_control():
    kc = KeyboardControl(stage, KeyloopKeyboardBindings())
    kc.loop()


def auto_calibration_callback(stage, daq, circuit, controller) -> None:
    """
    Moves to the specified circuit and optimizes alignment.

    Parameters
    ----------
    stage : Stage
        The stage to move.
    daq : DataAcquisitionUnitBase
        The DAQ to use for data acquisition.
    circuit : Circuit
        The circuit being moved to for calibration.
    controller : KeyboardControl
        The controller to use for control input.
    """
    print(f"Center {circuit} in view, then quit the controller.")
    print(f"GDS loc: {circuit.loc}")

    SCAN_SPAN = 0.035
    SCAN_STEP = 0.0024

    while True:
        print("Entering control loop")
        controller.loop()

        print("Optimizing alignment...")
        auto_scan(stage=stage, daq=daq, span=SCAN_SPAN, step_size=SCAN_STEP, plot=True, go_to_max=True)
        
        scan_again = input("Move to new location and scan again? (y/n) [Enter]: ")
        if scan_again == 'y':
            continue
        else:
            break
    print("DONE")


if __name__ == "__main__":
    cmap = CircuitMap.loadtxt("data/circuitmap.txt")
    calib = cmap.filterby(calibration_circuit="True")

    scfg = load_default_configuration()
    stage = scfg.get_stage()

    scope_configure_single_meas()
    laser_configure()

    SCAN_SPAN = 0.06
    SCAN_STEP = 0.0024

    def do_auto_scan():
        auto_scan(stage=stage, daq=stage.scope, span=SCAN_SPAN, step_size=SCAN_STEP, go_to_max=True)

    def do_basic_scan():
        return basic_scan(stage=stage, daq=stage.scope, span=SCAN_SPAN, step_size=SCAN_STEP, plot=True)

    def do_auto_scan():
        return auto_scan(stage=stage, daq=stage.scope, settle=0.0, plot=True, go_to_max=True)

    def do_calibration():
        return calibrate(stage=stage, daq=stage.scope, circuits=calib, callback=auto_calibration_callback)

    def do_easy_switcher():
        return easy_switcher(stage=stage, daq=stage.scope)

    # pos = {}
    pos = {1: [1.1629, 3.1288, None, None, None, 100.0], 2: [10.0975, 3.3209, None, None, None, 100.0], 3: [9.9237, 11.5935, None, None, None, 100.0]}
    stage.set_position(x=9.90561, y=11.60072)
    do_auto_scan()
    
    # cmat = do_calibration()
    # print(cmat)
    # calibrate(stage, stage.scope, calib, auto_calibration_callback)
