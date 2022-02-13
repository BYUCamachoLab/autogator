<p align="center">
<img src="https://raw.githubusercontent.com/BYUCamachoLab/autogator/master/docs/images/autogator.png" width="40%" alt="PyroLab">
</p>

<p align="center">
<img alt="Development version" src="https://img.shields.io/badge/master-v0.3.0-informational">
<a href="https://pypi.python.org/pypi/autogator"><img alt="PyPI Version" src="https://img.shields.io/pypi/v/autogator.svg"></a>
<img alt="PyPI - Python Version" src="https://img.shields.io/pypi/pyversions/autogator">
<a href="https://autogator.readthedocs.io/"><img alt="Documentation Status" src="https://readthedocs.org/projects/autogator/badge/?version=latest"></a>
<a href="https://pypi.python.org/pypi/autogator/"><img alt="License" src="https://img.shields.io/pypi/l/autogator.svg"></a>
<a href="https://github.com/BYUCamachoLab/autogator/commits/master"><img alt="Latest Commit" src="https://img.shields.io/github/last-commit/BYUCamachoLab/autogator.svg"></a>
</p>

# Autogator 

The Automatic Chip Interrogator, by Sequoia Ploeg ([BYU CamachoLab](https://camacholab.byu.edu/)).

A software package for camera-assisted motion control and experiment 
configuration of photonic integrated circuit interrogation platforms.

## Installation

This package is cross-platform and can be installed on any operating system.

AutoGator is a client with algorithms for interacting with instruments 
controlled by other softwares. It typically communicates with hardware using
socket connections.

It is recommended to use a virtual environment when installing Autogator. 
To recreate the development environment, after manually installing the above packages, run:

```
pip install -r requirements.txt
```

## Dev Notes

### Possible algorithm for calibrating the stage

* Home the stages
* Open up a controller to move the stage to some beginning position with some item on the screen
* Make sure the zoom is set to 1x, or know what the zoom level is
* Move the controller some distance in x, whether in the controller or predefined
* Click where the object has moved to
* Move the controller some distance in y, whether in the controller or predefined
* Click where the object has moved to
* Calculate the number of pixels and equate it to some physical distance