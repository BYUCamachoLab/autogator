# Listing of AutoGator Configuration Options

This is a comprehensive list of all configuration parameters. For now, it 
includes parameters that aren't necessarily meant to be edited by humans, such
as "last modified" times. 


## Hardware Configurations

* "hardware.stagex.available": bool - Motorized x-stage is present
* "hardware.stagey.available": bool - Motorized y-stage is present
* "hardware.stagez.available": bool - Motorized z-stage is present
* "hardware.stagerot.available": bool - Motorized rotational stage is present

## Software Configurations

* "logging.level": str - Log level

## AutoGator Configurations (not for humans!)

* "stage.lastCalibrated": str - The datetime of the last calibration
* "stage.lastHomed": str - The datetime of the last homing
