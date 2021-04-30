from packages.motion import *
from packages.dataScanner import DataScanner
from packages.map import Map
from packages.platformCalibrator import PlatformCalibrator
import os
from pathlib import Path
import time
import sys
from datetime import datetime
from pyrolab.drivers.lasers.tsl550 import TSL550
from pyrolab.drivers.scopes.rohdeschwarz import RTO
from pyrolab.analysis import WavelengthAnalyzer

import os
os.add_dll_directory("C:\\Program Files\\Thorlabs\\Kinesis")

class Test:
    def __init__(self, lambda_start=1500, lambda_stop=1600, duration=15, trigger_step=0.1, power_dBm=12, sample_rate=10e9, buffer=2,
    filename_prefix="", filename_suffix="data_now", data_directory="measurements/", append_date=True, save_raw_data=True,
    take_screenshot=True, active_channels=[1,2,3,4], trigger_channel=1, trigger_level=1, 
    scope_IP="10.32.112.162", scope_protocol="INSTR", scope_range_1=10, scope_range_2=5, scope_range_3=5, scope_range_4=5, 
    scope_position_1=2, scope_position_2=-4, scope_position_3=-2, scope_position_4=.5):
        self.lambda_start    = lambda_start
        self.lambda_stop     = lambda_stop
        self.duration        = duration
        self.trigger_step    = trigger_step
        self.power_dBm       = power_dBm
        self.sample_rate     = sample_rate
        self.sweep_rate = (lambda_stop - lambda_start) / duration
        self.buffer          = buffer #Additional time around duration to prevent timeout
        self.filename_prefix = filename_prefix
        self.filename_suffix = filename_suffix
        self.data_directory  = data_directory
        self.append_date     = append_date #Appends date to the beginning of the directory.
        self.save_raw_data   = save_raw_data #Save raw data collected from devices.
        self.take_screenshot = take_screenshot
        self.active_channels = active_channels #Channels to activate and use.
        self.trigger_channel = trigger_channel #Channel for trigger signal.
        self.trigger_level   = trigger_level #Voltage threshold for postitive slope edge trigger.
        self.scope_IP = scope_IP
        self.scope_protocol = scope_protocol
        self.channel_setting = {
            #Additional settings to pass to each channel if used.
            1: {"range": scope_range_1, "position": scope_position_1}, 
            2: {"range": scope_range_2, "position": scope_position_2},
            3: {"range": scope_range_3, "position": scope_position_3},
            4: {"range": scope_range_4, "position": scope_position_4}
        }

    def run(self):
        # ---------------------------------------------------------------------------- #
        # Check Input
        # ---------------------------------------------------------------------------- #
        # Get command line arguments.
        args = sys.argv[1:]
        filename = self.filename_prefix + sys.argv[0] + self.filename_suffix


        # ---------------------------------------------------------------------------- #
        # Initialize Save Directory
        # ---------------------------------------------------------------------------- #
        today = datetime.now()
        datePrefix = "{}_{}_{}_{}_{}_".format(today.year, today.month, today.day, today.hour, today.minute)
        prefix = datePrefix if self.append_date else ""
        folderName = prefix + self.data_directory
        folderPath = Path(Path.cwd(), folderName)
        print("Saving data to {} in current directory.".format(folderName))
        if not os.path.exists(folderPath):
            print("Creating {} directory.".format(folderName))
            os.makedirs(folderPath)


        # ---------------------------------------------------------------------------- #
        # Initialize Devices
        # ---------------------------------------------------------------------------- #
        # Initialize Laser
        print("Initializing laser.")
        try:
            # Remote Computer via PyroLab
            from pyrolab.api import locate_ns, Proxy
            ns = locate_ns(host="camacholab.ee.byu.edu")
            laser = Proxy(ns.lookup("TSL550"))
        except:
            # Local Computer
            laser = TSL550("COM4")

        laser.start()
        laser.on()
        laser.power_dBm(self.power_dBm)
        laser.open_shutter()
        laser.sweep_set_mode(continuous=True, twoway=True, trigger=False, const_freq_step=False)
        print("Enabling laser's trigger output.")
        laser.trigger_enable_output()
        triggerMode = laser.trigger_set_mode("Step")
        triggerStep = laser.trigger_set_step(self.trigger_step)
        print("Setting trigger to: {} and step to {}".format(triggerMode, self.triggerStep))

        #Get number of samples to record. Add buffer just in case.
        acquire_time = self.duration + self.buffer
        numSamples = int((acquire_time) * self.sample_rate)
        print("Set for {:.2E} Samples @ {:.2E} Sa/s.".format(numSamples, self.sample_rate))


        #Oscilloscope Settings
        print("Initializing Oscilloscope")
        scope = RTO(self.scope_IP, protocol=self.scope_protocol)
        scope.acquisition_settings(self.sample_rate, acquire_time)
        for channel in self.active_channels:
            channelMode = "Trigger" if (channel == self.trigger_channel) else "Data"
            print("Adding Channel {} - {}".format(channel, channelMode))
            scope.set_channel(channel, **self.channel_setting[channel])
        #Add trigger.
        print("Adding Edge Trigger @ {} Volt(s).".format(self.trigger_level))
        scope.edge_trigger(self.trigger_channel, self.trigger_level)


        # ---------------------------------------------------------------------------- #
        # Collect Data
        # ---------------------------------------------------------------------------- #
        print('Starting Acquisition')
        scope.start_acquisition(timeout = self.duration*3)

        print('Sweeping Laser')
        laser.sweep_wavelength(self.lambda_start, self.lambda_stop, self.duration)

        print('Waiting for acquisition to complete.')
        scope.wait_for_device()

        if self.take_screenshot:
            scope.screenshot(folderName + "screenshot.png")

        #Acquire Data
        rawData = [None] #Ugly hack to make the numbers line up nicely.
        rawData[1:] = [scope.get_data_ascii(channel) for channel in self.active_channels]
        wavelengthLog = laser.wavelength_logging()
        wavelengthLogSize = laser.wavelength_logging_number()

        #Optional Save Raw Data
        if self.save_raw_data:
            print("Saving raw data.")
            for channel in self.active_channels:
                with open(folderName + "CHAN{}_Raw.txt".format(channel), "w") as out:
                    out.write(str(rawData[channel]))
            with open(folderName + "Wavelength_Log.txt", "w") as out:
                out.write(str(wavelengthLog))

        # ---------------------------------------------------------------------------- #
        # Process Data
        # ---------------------------------------------------------------------------- #
        print("Processing Data")
        analysis = WavelengthAnalyzer(
            sample_rate = self.sample_rate,
            wavelength_log = wavelengthLog,
            trigger_data = rawData[self.trigger_channel]
        )

        print('=' * 30)
        print("Expected number of wavelength points: " + str(int(wavelengthLogSize)))
        print("Measured number of wavelength points: " + str(analysis.num_peaks()))
        print('=' * 30)

        data = [None] #Really ugly hack to make index numbers line up.
        data[1:] = [
            #List comprehension to put all the datasets in this one array.
            analysis.process_data(rawData[channel]) for channel in self.active_channels
        ]

        print("Raw Datasets: {}".format(len(rawData)))
        print("Datasets Returned: {}".format((len(data))))

        # ---------------------------------------------------------------------------- #
        # Generate Visuals & Save Data
        # ---------------------------------------------------------------------------- #
        for channel in self.active_channels:
            if (channel != self.trigger_channel):
                print("Displaying data for channel " + str(channel))
                ###VisualizeData(folderName + filename, channel, **(data[channel]))
