import PIL.Image
import os

def get_image_by_name(filename):
    return PIL.Image.open(os.path.join(os.path.dirname(__file__), filename))