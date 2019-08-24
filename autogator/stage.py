import thorlabs_apt as apt
import numpy as np

import autogator.configurations as config

stage_motor_x = apt.Motor(config.stage_x)
stage_motor_y = apt.Motor(config.stage_y)