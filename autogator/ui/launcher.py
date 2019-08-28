import os
from tkinter import *
from tkinter.ttk import *

import autogator.ui


class Launcher(autogator.ui.Window):
    def __init__(self, master, **kwargs):
        super().__init__(master, title='AutoGator Launcher', **kwargs)
        self.frame = Frame(master)
        self.frame.pack()
        self.button = Button(self.frame, text='Launch Camera', command=self.video)
        self.button.pack()

    def video(self):
        import autogator.ui.video
        camera = autogator.ui.video.SelectCameraDialog(Toplevel(self.master)).selected_camera()
        # if camera is None:
        #     return
        try:
            self.video.master.focus()
        except:
            self.video = autogator.ui.video.VideoWindow(Toplevel(self.master), source=camera)
            self.video.master.focus()
