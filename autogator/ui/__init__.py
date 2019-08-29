import os
import autogator

class Window(object):
    def __init__(self, master, title=None, icon='default.ico', **kwargs):
        self.master = master
        self.master.title(title if title is not None else "tk")
        self.master.iconbitmap(os.path.join(os.path.dirname(autogator.__file__), 'images', icon))

    def center(self):
        self.master.update_idletasks()
        width = self.master.winfo_width()
        height = self.master.winfo_height()
        x = (self.master.winfo_screenwidth() // 2) - (width // 2)
        y = (self.master.winfo_screenheight() // 2) - (height // 2)
        self.master.geometry('{}x{}+{}+{}'.format(width, height, x, y))