import datetime
from pathlib import Path
from typing import List

from pyrolab.analysis import WavelengthAnalyzer

from autogator.experiment import Experiment, ExperimentRunner


channel_settings = {
    1: {"range": 10, "position": 2},
    2: {"range": 0.2, "position": -4},
    3: {"range": 0.2, "position": -2},
    4: {"range": 0.2, "position": 0.5},
}

wl_start: float = 1500
wl_stop: float = 1600
duration: float = 5.0
sample_rate: float = 3
trigger_step: float = 0.01
power_dBm: float = 12.0
buffer: float = 5.0
active_channels: List[int] = [1, 2, 3, 4]
trigger_channel: int = 1
trigger_level: int = 1
take_screenshot: bool = True
save_raw_data: bool = True
filename: str = "data"
chip_name: str = "chipname"

FILE_PREFIX = f"""
# Test performed at {"None"}
# WL start: {wl_start} nm
# WL end: {wl_stop} nm
# Laser power: {power_dBm} dBm
#
# Wavelength\tCh1\tCh2\tCh3\tCh4
"""


class WavelengthSweepExperiment(Experiment):
    """
    A wavelength sweep experiment keeps laser power constant, but changes the
    wavelength of the laser. As the laser sweeps, it outputs a trigger signal
    and logs wavelength points. The trigger signal is collected on the
    oscilloscope, which collects data for the entire duration of the sweep,
    and the time-based data is then correlated to the wavelengths as denoted
    by the trigger signal. The data is saved to a text file.

    Parameters
    ----------
    wl_start : float
        The starting wavelength of the sweep.
    wl_stop : float
        The ending wavelength of the sweep.
    duration : float
        The duration of the sweep, in seconds. This will define the sweep rate.
    sample_rate : float
        The sample rate of the oscilloscope.
    trigger_channel : int
        The channel on the oscilloscope that will be used to trigger the data
        collection. This is the laser's output trigger that correlates time
        to logged wavelengths.
    power_dBm : float
        The power of the laser, in dBm.
    buffer : float
        The number of seconds to buffer after collecting data before raising
        a timeout error from the scope.
    active_channels : List[int]
        The oscilloscope channels to collect data on (1-indexed).
    trigger_channel : int
        The channel the laser trigger is conneceted to.
    trigger_level : float
        The trigger voltage to begin data collection at.
    output_dir : str
        The directory to save the data to.
    take_screenshot : bool
        Whether or not to take a screenshot of the waveform.
    save_raw_data : bool
        Whether or not to save the raw data to a file.
    filename : str
    chip_name : str
    """
    def setup(self):
        self.laser = self.stage.laser
        self.scope = self.stage.scope

        self.laser.start()
        self.laser.on()

        sweep_rate = (wl_stop - wl_start) / duration
        assert sweep_rate > 1.0
        assert sweep_rate < 100.0
        assert wl_start >= 1500  # self.laser.MINIMUM_WAVELENGTH
        assert wl_stop <= 1630  # self.laser.MAXIMUM_WAVELENGTH

        self.laser.power_dBm(power_dBm)
        self.laser.open_shutter()
        self.laser.sweep_set_mode(
            continuous=True, twoway=True, trigger=False, const_freq_step=False
        )

        print("Enabling self.laser's trigger output.")
        triggerMode, triggerStep = self.laser.set_trigger("Step", trigger_step)
        # self.laser.trigger_enable_output()
        # triggerMode = self.laser.trigger_set_mode("Step")
        # triggerStep = self.laser.trigger_set_step(self.trigger_step)
        print("Setting trigger to: {} and step to {}".format(triggerMode, triggerStep))

        acquire_time = duration + buffer
        numSamples = int((acquire_time) * sample_rate)
        print(
            "Set for {:.2E} Samples @ {:.2E} Sa/s.".format(numSamples, sample_rate)
        )

        self.scope.acquisition_settings(sample_rate=sample_rate, duration=acquire_time)
        for channel in active_channels:
            channelMode = "Trigger" if (channel == trigger_channel) else "Data"
            print("Adding Channel {} - {}".format(channel, channelMode))
            self.scope.set_channel(channel, **channel_settings[channel])

    def run(self):
        # self.experiment.set_filename("fabrun5", circuit.loc[0], circuit.loc[1])
        # auto-optimize

        print("Adding Edge Trigger @ {} Volt(s).".format(trigger_level))
        self.scope.edge_trigger(trigger_channel, trigger_level)

        print("Starting Acquisition")
        self.scope.acquire(timeout=duration * 2)

        print("Sweeping laser")
        self.laser.sweep_wavelength(wl_start, wl_stop, duration)

        print("Waiting for acquisition to complete...")
        self.scope.wait_for_device()

        # if self.take_screenshot:
        #     self.scope.screenshot(self.output_dir, self.filename + "_screenshot.png")

        print("Getting raw data...")
        raw = {
            channel: self.scope.get_data(channel) for channel in active_channels
        }
        wavelengthLog = self.laser.wavelength_logging()

        print("Processing Data")
        analysis = WavelengthAnalyzer(
            sample_rate=self.sample_rate,
            wavelength_log=wavelengthLog,
            trigger_data=raw[self.trigger_channel],
        )

        sorted_data = {
            channel: analysis.process_data(raw[channel])
            for channel in self.active_channels
        }

        today = datetime.now()
        date_prefix = f"{today.year}_{today.month}_{today.day}_{today.hour}_{today.minute}_"
        output_dir = Path.home() / "Downloads" / "data"
        filename = output_dir / f"{date_prefix}_{chip_name}_locx_{self.circuit.loc.x}_locy_{self.circuit.loc.y}.wlsweep"
        
        print("Saving raw data.")
        with filename.open("w") as out:
            out.write(FILE_PREFIX)
            data_lists = [sorted_data[self.trigger_channel]["wavelengths"]]
            for channel in raw:
                data_lists.append(sorted_data[channel]["data"])
            data_zip = zip(*data_lists)
            for data_list in data_zip:
                for data in data_list:
                    out.write(str(data) + "\t")
                out.write("\n")

    def teardown(self):
        pass


if __name__ == "__main__":
    from autogator.circuit import CircuitMap
    cmap = CircuitMap.loadtxt("data/circuitmap.txt")

    mzi2 = cmap.filterby(name="MZI2")
    runner = ExperimentRunner(mzi2, WavelengthSweepExperiment)
    runner.run()
