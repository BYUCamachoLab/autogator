import os
import autogator

class Window(object):
    def __init__(self, master, title=None, icon='default.ico', **kwargs):
        self.master = master
        self.master.title(title if title is not None else "tk")
        self.master.iconbitmap(os.path.join(os.path.dirname(autogator.__file__), 'images', icon))
