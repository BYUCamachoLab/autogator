import numpy as np

class ImageGeneratorStub:
    _instance = None
    
    def __init__(self, width, height):
        if self._instance is not None:
            print("Problem.")
            raise RuntimeError('Resource already in use! Cannot be reused until released.')
        else:
            self._instance = self

        self.width = width
        self.height = height
        self.live_mode = False

    def start_live_video(self):
        self.live_mode = True

    def stop_live_video(self):
        self.live_mode = True

    def latest_frame(self):
        if self.live_mode is False:
            raise RuntimeError("Cannot get latest frame when camera is not in live mode.")
        return np.random.normal(size=(self.height, self.width, 3))

    def get_captured_image(self):
        return np.random.normal(size=(self.height, self.width, 3))

    def close(self):
        self._instance = None
        