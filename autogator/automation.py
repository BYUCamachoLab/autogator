import thorlabs_apt as apt
import numpy as np

import autogator.configurations as config
from autogator.MotionControl.Benchtop import Piezo
from autogator.MotionControl.KCube import DCServo

class ChipStage(object):
    def __init__(self):
        self.stage_motor_x = DCServo(config.stage_x)
        self.stage_motor_y = DCServo(config.stage_y)

        self._home()
        self.saved_locations = {}

    def _home(self):
        self.stage_motor_x.home()
        self.stage_motor_y.home()

    def get_position(self):
        '''
        Gets the (x, y) position of the stage.

        Returns
        -------
        out : tuple
            (x, y) positions of the stages.
        '''
        x = self.stage_motor_x.position
        y = self.stage_motor_y.position
        return (x, y)

    def set_position(self, x, y):
        '''
        Sets the (x, y) position of the stage.

        Parameters
        ----------
        x : float
            The x position of the stage.
        y : float
            The y position of the stage.
        '''
        self.stage_motor_x.move_to(x)
        self.stage_motor_y.move_to(y)

    def save_location(self):
        pass

    def move_to_saved_location(self):
        pass


class MotionManager(object):
    pass

# Algorithm for calibrating the stage
    # Home the stages
    # Open up a controller to move the stage to some beginning position with some item on the screen
    # Make sure the zoom is set to 1x, or know what the zoom level is
    # Move the controller some distance in x, whether in the controller or predefined
    # Click where the object has moved to
    # Move the controller some distance in y, whether in the controller or predefined
    # Click where the object has moved to
    # Calculate the number of pixels and equate it to some physical distance