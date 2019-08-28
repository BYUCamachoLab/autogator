from tkinter import *
from tkinter.ttk import *
import numpy as np
import threading
import PIL.Image, PIL.ImageTk
from enum import Enum

import autogator.ui
import autogator.stubs as camera

from instrumental import instrument
from instrumental.drivers.cameras import uc480

opened_instruments = {}

class ZoomMode(Enum):
    MATCH_WINDOW = 0
    MATCH_IMAGE = 1

class SelectCameraDialog(autogator.ui.Window):
    def __init__(self, master, **kwargs):
        super().__init__(master, title='Select Camera Device')
        self.master.protocol("WM_DELETE_WINDOW", self.on_cancel)
        self.options = []
        self.var = StringVar(self.master)

        self.paramsets = uc480.list_instruments()
        if len(self.paramsets) == 0:
            self.found_devices = False
            self.options.append("No devices detected")
        else:
            self.found_devices = True
            for item in self.paramsets:
                self.options.append(str(item))

        self.var.set(self.options[0])
        self.options_list = OptionMenu(self.master, self.var, *self.options)
        self.options_list.pack()
        
        buttons = Frame(self.master)
        buttons.pack(fill='x', expand=True)

        ok_btn = Button(buttons, text="OK", command=self.on_ok)
        ok_btn.pack(side=RIGHT)

        cancel_btn = Button(buttons, text='Cancel', command=self.on_cancel)
        cancel_btn.pack(side=RIGHT)

    def selected_camera(self):
        self.master.wait_window(self.master)
        if self.found_devices and self.success:
            idx = self.options.index(self.var.get())
            if str(self.paramsets[idx]) not in opened_instruments:
                opened_instruments[str(self.paramsets[idx])] = instrument(self.paramsets[idx])
            return opened_instruments[str(self.paramsets[idx])]
        else:
            return None

    def on_cancel(self):
        self.success = False
        self.master.destroy()
        
    def on_ok(self):
        self.success = True
        self.master.destroy()

class VideoWindow(autogator.ui.Window):
    def __init__(self, master, source=None, **kwargs):
        super().__init__(master, title='Live Video')

        self.menubar = Menu(self.master)
        self._setup_menubar()
        self.master.config(menu=self.menubar)

        self.frame = Frame(master, **kwargs)
        self.frame.pack(fill="both", expand=True)
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        if source is not None:
            self.camera = source
        else:
            self.camera = camera.ImageGeneratorStub(800, 600)
        
        self.camera.start_live_video()

        self.canvas = Canvas(self.frame, width=800, height=600) #, cursor='tcross', width=self.vid.width, height=self.vid.height
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Double-Button-1>", self.on_double_click)

        self.zoom_level = 1.0
        self.zoom_mode = ZoomMode.MATCH_IMAGE

        self.delay = 15
        self.update()

    def _setup_menubar(self):
        file_menu = Menu(self.menubar, tearoff=0)
        # Maybe camera connection will be sub to file_menu?
        self.menubar.add_cascade(label="File", menu=file_menu)
        camera_menu = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Camera", menu=camera_menu)

        edit_menu = Menu(self.menubar, tearoff=0)
        # Maybe zoom menu will be sub to edit_menu?
        self.menubar.add_cascade(label="Edit", menu=edit_menu)
        zoom_menu = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Zoom", menu=zoom_menu)
        
        actions_menu = Menu(self.menubar, tearoff=0)
        # Actions include snapshot, video capture, calibrate, cursor, etc.
        self.menubar.add_cascade(label="Actions", menu=actions_menu)

    def update(self):
        self.img = PIL.Image.fromarray(self.camera.latest_frame(), 'RGB')
        self.photo = PIL.ImageTk.PhotoImage(image=self.scale_image(self.img))
        self.canvas.create_image(0, 0, image=self.photo, anchor=NW)
        self.master.after(self.delay, self.update)

    def scale_image(self, img):
        if self.zoom_mode == ZoomMode.MATCH_IMAGE:
            w, h = img.size
            img = img.resize((int(w * self.zoom_level), int(h * self.zoom_level)), PIL.Image.ANTIALIAS)
        elif self.zoom_mode == ZoomMode.MATCH_WINDOW:
            maxsize = (self.canvas.winfo_width(), self.canvas.winfo_height())
            ratio = int(np.ceil(max([x for x in np.array(maxsize)/np.array(img.size)])))
            if ratio > 1:
                img = img.resize([(ratio * s) for s in img.size])            
            img.thumbnail(maxsize, PIL.Image.ANTIALIAS)
        return img

    def on_closing(self):
        self.camera.stop_live_video()
        self.camera.close()
        self.master.destroy()

    def on_double_click(self, event):
        print("Event coords:", event.x, event.y)
        canvas = event.widget
        x = canvas.canvasx(event.x)
        y = canvas.canvasy(event.y)
        print("Canvas coords:", x, y, canvas.find_closest(x, y))
    