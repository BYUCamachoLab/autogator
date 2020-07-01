# Autogator
The AUTOmatic chip interroGATOR.

A software package for camera-assisted motion control of PIC chip interrogation platforms.

## Notes
ThorLabs software, [Kinesis](https://www.thorlabs.com/newgrouppage9.cfm?objectgroup_id=10285) must be installed. 
You also need the [uc480 API](https://www.thorlabs.com/software_pages/ViewSoftwarePage.cfm?Code=ThorCam) installed.

This package only works on Windows.

This package makes use of the less restrictive PySide2 module for GUI creation.


### Possible algorithm for calibrating the stage

* Home the stages
* Open up a controller to move the stage to some beginning position with some item on the screen
* Make sure the zoom is set to 1x, or know what the zoom level is
* Move the controller some distance in x, whether in the controller or predefined
* Click where the object has moved to
* Move the controller some distance in y, whether in the controller or predefined
* Click where the object has moved to
* Calculate the number of pixels and equate it to some physical distance