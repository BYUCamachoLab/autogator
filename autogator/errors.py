# -*- coding: utf-8 -*-
#
# Copyright © Autogator Project Contributors
# Licensed under the terms of the GNU GPLv3+ License
# (see autogator/__init__.py for details)

"""
Errors
======

Custom errors for AutoGator.
"""

class AutogatorError(Exception):
    """
    Base class for all AutoGator errors.
    """
    pass


class UncalibratedStageError(AutogatorError):
    """
    Raised when commands requiring calibration are called on an uncalibrated 
    stage.
    """
    pass


class CircuitMapKeyError(AutogatorError):
    """
    Raised when a location key is not found in a circuit map.
    """
    pass


class CircuitMapUniqueKeyError(AutogatorError):
    """
    Raised when a location key is found in a circuit file more than once.
    """
    pass
