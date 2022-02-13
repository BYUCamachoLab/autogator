# -*- coding: utf-8 -*-
#
# Copyright © Autogator Project Contributors
# Licensed under the terms of the GPLv3+ License
# (see autogator/__init__.py for details)

"""
Basic Scan
----------

Basic scan example. Allows you to adjust the location of the stage and then
performs a basic, brute force grid scan about the location you stop at. Plots a
heatmap relating to the intensity of the light detected at each point on the
grid.

In this example, your stage configuration must include a data acquisition
object configuration as an auxiliary device for the stage. For this example,
our data acquisition unit is a digital oscilloscope. Because it conforms to the
standard autogator.hardware.DataAcquisitionUnitBase interface, it provides a
``measure()`` method that can is used to detect intensity at each grid point.

To run this script, simply run:

``` bash
$ python basic_scan.py
```

Note that the ``autogator.routines.basic_scan()`` function is super 
customizable. This example only uses the most basic parameters, but non-square
grids and different step sizes in x and y can be specified, see the 
function documentation for more details.
"""

from autogator.api import load_default_configuration
from autogator.controllers import KeyboardControl, KeyloopKeyboardBindings
from autogator.routines import basic_scan


stage = load_default_configuration().get_stage()

kc = KeyboardControl(stage, KeyloopKeyboardBindings())
kc.loop()

SCAN_SPAN = 0.06
SCAN_STEP = 0.0024

basic_scan(
    stage=stage,
    daq=stage.scope, 
    span=SCAN_SPAN, 
    step_size=SCAN_STEP, 
    plot=True
)
