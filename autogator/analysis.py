# -*- coding: utf-8 -*-
#
# Copyright © Autogator Project Contributors
# Licensed under the terms of the GNU GPLv3+ License
# (see autogator/__init__.py for details)

"""
# Analysis

A series of convenience functions for processing raw data.
"""

from typing import NamedTuple
import numpy as np
from scipy.signal import find_peaks


class AnalysisResult(NamedTuple):
    """
    A named tuple for storing analysis results.        

    Attributes
    ----------
    wl : ndarray
        Wavelength values.
    data : ndarray
        Corresponding data values.
    """
    wl: np.ndarray
    data: np.ndarray

    @property
    def wavelength_hash(self) -> str:
        """The hash of the wavelength data."""
        return hash(self.wl)

    @property
    def data_hash(self) -> str:
        """The hash of the raw data."""
        return hash(self.data)


class WavelengthAnalyzer:
    """
    Uses a trigger signal to convert datasets from time-domain to wavelength.

    Correlates a trigger signal, typically output from a laser, to a dataset.
    The laser logs the current wavelength each time the trigger is high.
    The trigger signal is expected to be a single channel of data as acquired
    by a data acquisition device. The wavelength sweep rate may not be constant 
    or linear in time. After receiving trigger data and the corresponding 
    wavelengths, a curve is fit to the wavelength as a function of time.
    Wavelengths for the raw data is then calculated by sampling the curve at
    the same time points as the raw data.

    Parameters
    ----------
    sample_rate : float
        The sample rate of the acquired data. Sample rate of the trigger signal
        should be the same as the sample rate of the raw data.
    trigger_data : ndarray
        The collected trigger signal. A peak finding algorithm is used to
        correlate time points to the wavelength log.
    wavelength_log : ndarray
        Log of wavelengths for each time the trigger signal was high.
    """
    def __init__(self, sample_rate: float, trigger_data: np.ndarray, wavelength_log: np.ndarray):
        self.sample_rate = sample_rate

        # Get indices of peaks in the trigger signal.
        self.peaks, _ = find_peaks(trigger_data, height=3, distance=15)

        # Make relative to the first point.
        mod_peaks = self.peaks - self.peaks[0]
        mod_time = mod_peaks / self.sample_rate
        fit = np.polyfit(mod_time, wavelength_log, 2) 
        
        # Create function mapping time to wavelength.
        self.mapping = np.poly1d(fit)

    def process_data(self, raw_data: np.ndarray) -> AnalysisResult:
        """
        Converts raw data to wavelength by interpolating against wavelength logs.

        Parameters
        ----------
        raw_data : ndarray
            The raw data to convert.

        Returns
        -------
        channel_data : dict
            A dictionary of processed data. Has the keys "wavelengths", "data",
            "wavelength_hash", and "data_hash".
        """
        data = raw_data[self.peaks[0]:self.peaks[-1]]
        
        # Time relative to the first collected data point.
        device_time = np.arange(len(data)) / self.sample_rate

        # Get wavelengths at given times.
        wls = self.mapping(device_time)

        return AnalysisResult(wls, data)
