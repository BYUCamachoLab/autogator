# -*- coding: utf-8 -*-
#
# Copyright © Autogator Project Contributors
# Licensed under the terms of the GPLv3+ License
# (see autogator/__init__.py for details)

"""
# Experiments

Sample WavelengthSweep experiment implementation.

This example uses the Santec TSL-550 as a laser, along with the Rohde & Schwarz
RTO2064 oscilloscope from PyroLab.
"""

from datetime import datetime
from getpass import getuser
from pathlib import Path
import time
import logging
from typing import List

import numpy as np

from autogator.analysis import WavelengthAnalyzer
from autogator.experiments import Experiment
from autogator.api import load_default_configuration
from autogator.routines import auto_scan


log = logging.getLogger(__name__)


class WavelengthSweepExperiment(Experiment):
    """
    A wavelength sweep experiment keeps laser power constant, but changes the
    wavelength of the laser. As the laser sweeps, it outputs a trigger signal
    and logs wavelength points. The trigger signal is collected on the
    oscilloscope, which collects data for the entire duration of the sweep,
    and the time-based data is then correlated to the wavelengths as denoted
    by the trigger signal. The data is saved to a text file.

    Attributes
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
    chip_name : str
        The name of the chip.
    """
    # General configuration
    MANUAL = False
    chip_name: str = "fabrun5"
    output_dir = Path("C:/Users/sequo/Documents/GitHub/autogator/examples/fake")

    # Scope configuration
    duration: float = 5.0
    buffer: float = 5.0
    sample_rate: int = int(np.floor(10e6 / (duration + buffer)))
    sample_rate = 1e5
    active_channels: List[int] = [1, 2]
    data_channels: List[int] = [2]
    trigger_channel: int = 1
    trigger_level: int = 1
    channel_settings = {
        1: {"range": 5, "position": -2.5},
        2: {"range": 0.6, "position": -4},
        # 3: {"range": 2.5, "position": -1},
        # 4: {"range": 2.5, "position": -1},
    }

    # Laser configuration
    wl_start: float = 1500
    wl_stop: float = 1600
    trigger_step: float = 0.01
    power_dBm: float = -4.0

    def setup(self):
        """
        Start up the laser and scope, enter details about who is running the
        experiment. Do some basic sanity checking on some values.
        """
        self.operator = input(f"Operator ({getuser()}) [ENTER]: ") 
        if not self.operator: 
            self.operator = getuser()

        self.laser = self.stage.laser.driver
        self.scope = self.stage.scope.driver

        self.laser._pyroClaimOwnership()
        self.laser.on()
        self.laser.open_shutter()

        sweep_rate = (self.wl_stop - self.wl_start) / self.duration
        assert sweep_rate > 1.0
        assert sweep_rate < 100.0
        assert self.wl_start >= 1500  # self.laser.MINIMUM_WAVELENGTH
        assert self.wl_stop <= 1630  # self.laser.MAXIMUM_WAVELENGTH

    def configure_scope_sweep(self):
        """
        The scope needs to be alternately configured to record a long sweep and
        a single-shot measurement. This function reconfigures for a long sweep.
        """
        acquire_time = self.duration + self.buffer
        numSamples = int((acquire_time) * self.sample_rate)
        print(
            "Set for {:.2E} Samples @ {:.2E} Sa/s.".format(numSamples, self.sample_rate)
        )

        self.scope.acquisition_settings(sample_rate=self.sample_rate, duration=acquire_time)
        for channel in self.active_channels:
            self.scope.set_channel(channel, **self.channel_settings[channel])
            time.sleep(0.1)

        self.scope.edge_trigger(self.trigger_channel, self.trigger_level)

    def configure_scope_measure(self):
        """
        The scope needs to be alternately configured to record a long sweep and
        a single-shot measurement. This function reconfigures for a single
        measurement.
        """
        MEAS_CHANNEL = 2
        RANGE = 2.0
        POSITION = -3.0

        self.scope.set_channel(1, range=RANGE, position=POSITION)
        self.scope.set_channel(2, range=RANGE, position=POSITION)
        self.scope.set_auto_measurement(source=F"C{MEAS_CHANNEL}W1")
        self.scope.wait_for_device()

        self.scope.edge_trigger(1, 0.0)
        self.scope.set_timescale(10e-10)
        self.scope.acquire(run="continuous")
        time.sleep(5)

    def configure_laser_sweep(self):
        """
        The laser needs to be alternately configured to sweep in wavelength and
        to return to the peak-power wavelength for alignment purposes. This
        function reconfigures for a wavelength sweep.
        """
        self.laser.power_dBm(self.power_dBm)
        self.laser.sweep_set_mode(
            continuous=True, twoway=True, trigger=False, const_freq_step=False
        )

        self.laser.trigger_enable_output()
        self.laser.trigger_set_mode("Step")
        self.laser.trigger_step(self.trigger_step)

    def configure_laser_measure(self):
        """
        The laser needs to be alternately configured to sweep in wavelength and
        to return to the peak-power wavelength for alignment purposes. This
        function reconfigures for a single measurement.
        """
        self.laser.wavelength(1550.0)

    def run(self):
        """
        The test procedure for every device under test.
        """
        print(self.circuit)

        self.configure_scope_measure()
        self.configure_laser_measure()

        # Maximize signal
        auto_scan(stage=self.stage, daq=self.stage.scope, settle=0.0, plot=self.MANUAL)

        self.configure_scope_sweep()
        self.configure_laser_sweep()

        log.debug("Starting Acquisition")
        self.scope.acquire(timeout=self.duration * 2)
        log.debug("Sweeping laser")
        self.laser.sweep_wavelength(self.wl_start, self.wl_stop, self.duration)
        log.debug("Waiting for acquisition to complete...")
        self.scope.wait_for_device()
        
        # Scope does provide the ability to save screenshots, if we want
        # scope.screenshot(screenshot_filename)

        log.debug("Downloading raw data...")
        raw = {}
        for channel in self.active_channels:
            raw[channel] = self.scope.get_data(channel)
        wavelengthLog = self.laser.wavelength_logging()

        print("Processing Data")
        analysis = WavelengthAnalyzer(
            sample_rate=self.sample_rate,
            wavelength_log=wavelengthLog,
            trigger_data=raw[self.trigger_channel],
        )

        sorted_data = {
            channel: analysis.process_data(raw[channel])
            for channel in self.data_channels
        }

        today = datetime.now()
        date_prefix = f"{today.year}_{today.month}_{today.day}_{today.hour}_{today.minute}_"
        filename = self.output_dir / f"{date_prefix}_{self.chip_name}_locx_{self.circuit.loc.x}_locy_{self.circuit.loc.y}".replace(".", "p")
        filename = filename.with_suffix(".wlsweep")
        
        FILE_HEADER = f"""Test performed at {today.strftime("%Y-%m-%d %H:%M:%S")}
Operator: {self.operator}
Chip: {self.chip_name}
Circuit: {self.circuit.loc.x}, {self.circuit.loc.y}
Laser power: {self.power_dBm} dBm
Wavelength start: {self.wl_start} nm
Wavelength stop: {self.wl_stop} nm

Wavelength\tCh1"""

        print("Saving raw data.")
        data_lists = []
        for channel in self.data_channels:
            if not data_lists:
                data_lists = [sorted_data[channel].wl]
            data_lists.append(sorted_data[channel].data)
        np.savetxt(filename, np.column_stack(data_lists), delimiter="\t", header=FILE_HEADER)

    def teardown(self):
        pass


if __name__ == "__main__":
    from autogator.circuits import CircuitMap
    from autogator.experiments import ExperimentRunner

    cmap = CircuitMap.loadtxt("data/circuitmap.txt")

    mzis = cmap.filterby(name="MZI4", grouping="1")
    stage = load_default_configuration().get_stage()
    
    try:
        runner = ExperimentRunner(mzis, WavelengthSweepExperiment, stage=stage)
        runner.run()
    except Exception as e:
        print(stage.scope.measure())
        raise e
