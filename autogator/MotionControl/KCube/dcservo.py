import thorlabs_apt as apt

class DCServo(apt.Motor):

    def __init__(self, serial_number):
        """
        Initializes the connection to the piezo controller. 
        
        Raises
        ------
        RuntimeError
            Raises a runtime error if the connection is unsuccessful.
        """
        super.__init__(self, serial_number)

    def get_travel_limits(self):
        min_position, max_position, _, _ = self.get_stage_axis_info()
        return (min_position, max_position)

    def home(self):
        """
        Home the device.
        """
        self.move_home()

    # TODO: Implement jog
    # def jog(self, direction):
    #     pass
