# Autogator 

The Automatic Chip Interrogator, by Sequoia Ploeg.

Version 0.3.0

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