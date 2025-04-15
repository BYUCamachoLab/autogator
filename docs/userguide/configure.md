# Configuring AutoGator

## Using a Network

The easiest way of configuring AutoGator is using a Python script, the
[`HardwareConfiguration`][autogator.hardware.HardwareConfiguration] and
[`StageConfiguration`][autogator.hardware.StageConfiguration] objects, and the
[`save_default_configuration()`][autogator.profiles.save_default_configuration]
function. This example assumes that you are using a PyroLab network of drivers
(see [PyroLab's documentation](https://pyrolab.readthedocs.io/en/latest/) for
more details).

``` python
import numpy as np

from autogator.api import save_default_configuration
from autogator.hardware import HardwareConfiguration, StageConfiguration
from autogator.profiles import update_calibration_matrix


x = HardwareConfiguration(
    classname="Z825BLinearStage",
    parameters={
        "pyroname": "xstage",
        "ns_host": "yourdomain.com",
    }
)
y = HardwareConfiguration(
    classname="Z825BLinearStage",
    parameters={
        "pyroname": "ystage",
        "ns_host": "yourdomain.com",
    }
)
scope = HardwareConfiguration(
    classname="RohdeSchwarzOscilloscope",
    parameters={
        "name": "oscope",
        "address": "1.2.3.4",
    }
)
laser = HardwareConfiguration(
    classname="TSL550Laser",
    parameters={
        "pyroname": "laser",
        "ns_host": "yourdomain.com",
    }
)

sc = StageConfiguration(
    x=x,
    y=y,
    auxiliaries={
        "laser": laser,
        "scope": scope,
    },
    calibration_matrix="./data/calib_mat.txt",
)

if __name__ == "__main__":
    save_default_configuration("mysetup", sc)
    matrix = np.loadtxt("data/calib_mat.txt")
    update_calibration_matrix("mysetup", matrix)
```

## Single-Machine Host and Client

If used as a single-machine host and client, PyroLab may simply be configured
to expose everything on localhost, including a nameserver, meaning no ports
will be exposed to any outside network. This may be useful in circumstances
where security is a concern or a single computer is powerful enough to host all
necessary resources. AutoGator can also then be configured to lookup and
connect to devices on the localhost network.

The script will look very similar, except in this case, "ns_host" should be
set to "localhost".
