# -*- coding: utf-8 -*-
#
# Copyright © Autogator Project Contributors
# Licensed under the terms of the GNU GPLv3+ License
# (see autogator/__init__.py for details)

"""
# Analysis

A series of convenience functions for processing raw data.
"""

import numpy as np
from scipy.signal import find_peaks


class WavelengthAnalyzer:
    """
    Uses a trigger signal to convert datasets from time-domain to wavelength.
    """
    def __init__(self, sample_rate, trigger_data, wavelength_log):
        self.sample_rate = sample_rate
        self.wavelength_log = wavelength_log
        self.__analyze_trigger(trigger_data)

        modPeaks = self.peaks - self.peaks[0] #Make relative to the first point.
        modTime = modPeaks / self.sample_rate
        fit = np.polyfit(modTime, self.wavelength_log, 2) #Least-squares fit.
        self.mapping = np.poly1d(fit) #Create function mapping time to wavelength.

    def __analyze_trigger(self, trigger_data):
        self.peaks, _ = find_peaks(trigger_data, height = 3, distance = 15)

    def process_data(self, raw_data):
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
        
        #Time relative to the first collected data point.
        deviceTime = np.arange(len(data)) / self.sample_rate

        wls = self.mapping(deviceTime) #Get wavelengths at given times.
        channel_data = {
            "wavelengths": wls,
            "data": data,
            "wavelength_hash": hash(tuple(wls)),
            "data_hash": hash(tuple(data))
        }
        return channel_data