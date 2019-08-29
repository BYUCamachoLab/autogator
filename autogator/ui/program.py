from tkinter import *
from tkinter.ttk import *
import numpy as np
import threading
import PIL.Image, PIL.ImageTk
from enum import Enum

import autogator
import autogator.ui
import autogator.stubs as camera

from instrumental import instrument
from instrumental.drivers.cameras import uc480

class ZoomMode(Enum):
    MATCH_WINDOW = 0
    MATCH_IMAGE = 1

class KCubeController(Frame):
    #
    # General GUI Organization and Layout
    #
    # +-----------------------------------------------------------------+
    # | title                                                           |
    # +-----------------------------------------------------------------+
    # | info_frame                                                      |
    # | +-------------------+-----------------------------------------+ |
    # | | position_frame    | details_frame                           | |
    # | |                   |                                         | |
    # | |                   |                                         | |
    # | |                   |                                         | |
    # | +-------------------+-----------------------------------------+ |
    # +-----------------------------------------------------------------+
    # | move_frame (grid inside)                                        |
    # +-----------------------------------------------------------------+
    def __init__(self, master, device='Controller', sn='N/A'):
        Style().configure('PosDisplay.TLabel', background='#2be32b', foreground='black')
        Frame.__init__(self, master, relief='ridge', borderwidth=15, width=250)
        title_str = device + " (s/n: " + str(sn) + ")"
        Label(self, text=title_str).pack(side=TOP, fill='x', expand=True)
        self.info_frame = Frame(self)
        Grid.columnconfigure(self.info_frame, 0, weight=3)
        Grid.columnconfigure(self.info_frame, 1, weight=1)
        Label(self.info_frame, text="Position").grid(row=0, column=0, sticky=W)
        Label(self.info_frame, text="21.04 mm", style='PosDisplay.TLabel').grid(row=1, column=0, rowspan=2, sticky=NSEW)
        Label(self.info_frame, text="Homed").grid(row=1, column=1)
        Button(self.info_frame, text="IDENT").grid(row=2, column=1)
        self.info_frame.pack(side=TOP, fill='x')
        self.move_frame = Frame(self)
        Grid.columnconfigure(self.info_frame, 0, weight=3)
        Grid.columnconfigure(self.info_frame, 1, weight=0)
        Label(self.move_frame, text="Move to:").grid(row=0, column=0, sticky=W)
        Entry(self.move_frame).grid(row=1, column=0, sticky=EW)
        Button(self.move_frame, text="GO").grid(row=1, column=1, sticky=NSEW)
        Label(self.move_frame, text="Move by:").grid(row=2, column=0, sticky=W)
        Entry(self.move_frame).grid(row=3, column=0, sticky=EW)
        Button(self.move_frame, text="GO").grid(row=3, column=1, sticky=NSEW)
        self.move_frame.pack(side=TOP, fill='x')
        self.pack(side=TOP, fill='x')


class AutoGatorWindow(autogator.ui.Window):
    #
    # General GUI Organization and Layout
    #
    # +-----------------------------------------------------------------+
    # | menubar                                                         |
    # +-----------------------------------------------------------------+
    # | tools_frame                                                     |
    # +-----------------------------------------------------------------+
    # | content_frame                                                   |
    # | +-------------------+-----------------------------------------+ |
    # | | controls_frame    | video_frame                             | |
    # | |                   |                                         | |
    # | |                   |                                         | |
    # | |                   |                                         | |
    # | +-------------------+-----------------------------------------+ |
    # +-----------------------------------------------------------------+
    # | status_frame                                                    |
    # +-----------------------------------------------------------------+

    def __init__(self, master, **kwargs):
        super().__init__(master, title='AutoGator')
        
        s = Style()
        s.configure('StatusBar.TFrame', background='#007acc', foreground='white')
        s.configure('StatusBar.TLabel', background='#007acc', foreground='white')
        s.configure('Controllers.TFrame', background='#252526', foreground='white')
        s.configure('Tools.TFrame', background='#3c3c3c', foreground='white')

        self.menubar = Menu(self.master)
        self._setup_menubar()
        self.master.config(menu=self.menubar)

        self.status_frame = Frame(master, height=20, borderwidth=2, style='StatusBar.TFrame')
        self.status_frame.pack(side=BOTTOM, fill="x", expand=False)
        self.status = "Ready"
        Label(self.status_frame, text=self.status, style='StatusBar.TLabel').pack(side=LEFT)

        self.tools_frame = Frame(master, height=50, borderwidth=15, style='Tools.TFrame')
        self.tools_frame.pack(side=TOP, fill='x', expand=False)

        self.content_frame = Frame(master)
        self.content_frame.pack(side=TOP, fill='both', expand=True)

        self.controls_frame = Frame(self.content_frame, width=250, borderwidth=15, style='Controllers.TFrame')
        self.controls_frame.pack(side=LEFT, fill='y', expand=False)
        # self.controls_frame.pack_propagate(False)
        self.controls_frame_items = []
        self.controls_frame_items.append(KCubeController(self.controls_frame, "X Stage"))
        self.controls_frame_items.append(KCubeController(self.controls_frame, "Y Stage"))

        self.video_frame = Frame(self.content_frame)
        self.video_frame.pack(side=LEFT, fill="both", expand=True)

        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.camera = camera.ImageGeneratorStub(800, 600)
        
        self.camera.start_live_video()
        w, h = PIL.Image.fromarray(self.camera.latest_frame(), 'RGB').size

        self.canvas = Canvas(self.video_frame, width=w, height=h) #, cursor='tcross', width=self.vid.width, height=self.vid.height
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
        self.img = self.scale_image(PIL.Image.fromarray(self.camera.latest_frame(), 'RGB'))
        self.photo = PIL.ImageTk.PhotoImage(image=self.img)
        self.canvas.create_image(0, 0, image=self.photo, anchor=NW)
        self.master.after(self.delay, self.update)

    def scale_image(self, img):
        if self.zoom_mode == ZoomMode.MATCH_IMAGE:
            w, h = img.size
            img = img.resize((int(w * self.zoom_level), int(h * self.zoom_level)), PIL.Image.ANTIALIAS)
        elif self.zoom_mode == ZoomMode.MATCH_WINDOW:
            # maxsize = (self.video_frame.winfo_width(), self.video_frame.winfo_height())
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
        framesize = (self.video_frame.winfo_width(), self.video_frame.winfo_height())
        maxsize = (self.canvas.winfo_width(), self.canvas.winfo_height())
        print("Framesize:", *framesize, " | ", "Canvassize:", maxsize)
        canvas = event.widget
        x = canvas.canvasx(event.x)
        y = canvas.canvasy(event.y)
        print("Canvas coords:", x, y, " | ", "Event coords:", event.x, event.y, " | ", "Image size:", *self.img.size)
    