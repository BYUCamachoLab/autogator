from typing import Dict, Any

from autogator.experiment import Experiment
from pyrolab.analysis import WavelengthAnalyzer
from datetime import datetime


class WavelengthSweepExperiment(Experiment):
    def __init__(
        self,
        wl_start: float=1500,
        wl_stop: float=1600,
        duration: float=5.0,
        sample_rate: float=1, 
        trigger_step: float=0.01,
        power_dBm: float=12.0,
        buffer: float=4.0,
        active_channels: list[int]=[1, 2, 3, 4],
        trigger_channel: int=1,
        trigger_level: int=1,
        output_dir: str="C:\\Users\\camacho\\autogator\\autogator\\data\\",
        take_screenshot: bool=True,
        save_raw_data: bool=True,
        filename: str="data",
        chip_name: str="chipname",
        ):
        super().__init__()
        self.channel_settings = {
            1: {"range": 10, "position": 2}, 
            2: {"range": .2, "position": -4},
            3: {"range": .2, "position": -2},
            4: {"range": .2, "position": 0.5},
        }
        self.wl_start = wl_start
        self.wl_stop = wl_stop
        self.duration = duration
        self.sample_rate = sample_rate
        self.trigger_step = trigger_step
        self.power_dBm = power_dBm
        self.buffer = buffer
        self.active_channels = active_channels
        self.trigger_channel = trigger_channel
        self.trigger_level = trigger_level
        self.take_screenshot = take_screenshot
        self.save_raw_data = save_raw_data
        self.output_dir = output_dir
        self.chip_name = chip_name
        today = datetime.now()
        self.date_prefix = "{}_{}_{}_{}_{}_".format(today.year, today.month, today.day, today.hour, today.minute)
        self.filename = "{}_{}_locx_ex_locy_ex.wlsweep".format(self.date_prefix, self.chip_name)
        self.file_prefix = "# Test performed at {}\n# WL start: {}nm\n# WL end: {}nm\n# laser power: {}dBm\n\n# Wavelength    Ch1 Ch2 Ch3 Ch4\n".format(self.date_prefix, self.wl_start, self.wl_stop, self.power_dBm)
   
    def set_filename(self, chip_name, loc_x, loc_y):
        today = datetime.now()
        self.date_prefix = "{}_{}_{}_{}_{}_".format(today.year, today.month, today.day, today.hour, today.minute)
        self.filename = "{}_{}_locx_{}_locy_{}".format(self.date_prefix, chip_name, loc_x, loc_y)
        self.filename = self.filename.replace(".", ",")

    def configure_channel(self, channel: int, params: Dict[str, Any]):
        self.channel_settings[channel] = params

    def run(self):
        laser = self.dataCache.get_laser()
        scope = self.dataCache.get_scope()

        sweep_rate = (self.wl_stop - self.wl_start) / self.duration
        assert sweep_rate > 1.0 
        assert sweep_rate < 100.0
        assert self.wl_start >= 1500 #laser.MINIMUM_WAVELENGTH
        assert self.wl_stop <= 1630 #laser.MAXIMUM_WAVELENGTH
        
        laser.start()
        laser.on()
        laser.power_dBm(self.power_dBm)
        laser.open_shutter()
        laser.sweep_set_mode(continuous=True, twoway=True, trigger=False, const_freq_step=False)
        print("Enabling laser's trigger output.")
        laser.trigger_enable_output()
        triggerMode = laser.trigger_set_mode("Step")
        triggerStep = laser.trigger_set_step(self.trigger_step)
        print("Setting trigger to: {} and step to {}".format(triggerMode, triggerStep))
         
        acquire_time = self.duration + self.buffer
        numSamples = int((acquire_time) * self.sample_rate)
        print("Set for {:.2E} Samples @ {:.2E} Sa/s.".format(numSamples, self.sample_rate))

        scope.acquisition_settings(self.sample_rate, acquire_time)
        for channel in self.active_channels:
            channelMode = "Trigger" if (channel == self.trigger_channel) else "Data"
            print("Adding Channel {} - {}".format(channel, channelMode))
            scope.set_channel(channel, **self.channel_settings[channel])
        print("Adding Edge Trigger @ {} Volt(s).".format(self.trigger_level))
        scope.edge_trigger(self.trigger_channel, self.trigger_level)

        print('Starting Acquisition')
        scope.acquire(timeout = self.duration*3)

        print('Sweeping Laser')
        laser.sweep_wavelength(self.wl_start, self.wl_stop, self.duration)

        print('Waiting for acquisition to complete...')
        scope.wait_for_device()

        if self.take_screenshot:
            scope.screenshot(self.output_dir + self.filename + "_screenshot.png")

        print("Getting raw data...")
        raw = {channel: scope.get_data(channel) for channel in self.active_channels}
        wavelengthLog = laser.wavelength_logging()
        wavelengthLogSize = laser.wavelength_logging_number() 

        if self.save_raw_data:
            print("Saving raw data.")
            with open(self.output_dir + self.filename + ".wlsweep", "w") as out:
                out.write(self.file_prefix)
                data_lists = [wavelengthLog]
                for channel in raw:
                    data_lists.append(raw[channel])
                data_zip = zip(*data_lists)
                for data_list in data_zip:
                    for data in data_list:
                        out.write(str(data) + "\t")
                    out.write("\n")

        laser.close()

if __name__ == "__main__":
    exp = WavelengthSweepExperiment()
    exp.run()