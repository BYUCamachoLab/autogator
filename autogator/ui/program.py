from tkinter import *
from tkinter.ttk import *
import numpy as np
import threading
import PIL.Image, PIL.ImageTk
from enum import Enum
import time

import autogator
import autogator.ui
import autogator.stubs as camera
import autogator.MotionControl.KCube
import autogator.configurations

from instrumental import instrument
from instrumental.drivers.cameras import uc480

class ThreadedRepeatingEvent(object):
    def __init__(self, target=None, args=None, delay=None, daemon=True):
        self.target = target
        self.args = args
        self.thread = threading.Thread(target=self._exec, daemon=daemon)
        self.delay = delay
        self.ticker = threading.Event()

    def start(self):
        self.thread.start()

    def _exec(self):
        while not self.ticker.wait(self.delay):
            if self.args:
                self.target(*self.args)
            else:
                self.target()

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
    def __init__(self, master, device='Controller', sn: int=None):
        Style().configure('PosDisplay.TLabel', background='#2be32b', foreground='black')
        Frame.__init__(self, master, relief='ridge', borderwidth=15, width=250)

        if sn is not None:
            try:
                self.motor = autogator.MotionControl.KCube.DCServo(sn)
            except:
                self.motor = None
                sn = "N/A"
        else:
            self.motor = None
            sn = "N/A"
        
        title_str = device + " (s/n: " + str(sn) + ")"
        Label(self, text=title_str).pack(side=TOP, fill='x', expand=True)
        
        self.info_frame = Frame(self)
        Grid.columnconfigure(self.info_frame, 0, weight=3)
        Grid.columnconfigure(self.info_frame, 1, weight=1)
        Label(self.info_frame, text="Position").grid(row=0, column=0, sticky=W)
        self.position = StringVar()
        Label(self.info_frame, textvariable=self.position, style='PosDisplay.TLabel').grid(row=1, column=0, rowspan=2, sticky=NSEW)
        Label(self.info_frame, text="Homed").grid(row=1, column=1)
        Button(self.info_frame, text="IDENT").grid(row=2, column=1)
        self.info_frame.pack(side=TOP, fill='x')
        
        self.move_frame = Frame(self)
        Grid.columnconfigure(self.info_frame, 0, weight=3)
        Grid.columnconfigure(self.info_frame, 1, weight=0)
        Label(self.move_frame, text="Move to:").grid(row=0, column=0, sticky=W)
        self.move_to_val = Entry(self.move_frame)
        self.move_to_val.grid(row=1, column=0, sticky=EW)
        self.move_to_val.bind('<Return>', self.move_to)
        self.move_to_val.bind('<KP_Enter>', self.move_to)
        Button(self.move_frame, text="GO", command=self.move_to).grid(row=1, column=1, sticky=NSEW)
        Label(self.move_frame, text="Move by:").grid(row=2, column=0, sticky=W)
        self.move_by_val = Entry(self.move_frame)
        self.move_by_val.grid(row=3, column=0, sticky=EW)
        self.move_by_val.bind('<Return>', self.move_by)
        self.move_by_val.bind('<KP_Enter>', self.move_by)
        Button(self.move_frame, text="GO", command=self.move_by).grid(row=3, column=1, sticky=NSEW)
        self.move_frame.pack(side=TOP, fill='x')
        
        self.pack(side=TOP, fill='x')

        refresh_period = 0.07
        ThreadedRepeatingEvent(target=self.update, delay=refresh_period, daemon=True).start()

    def update(self):
        if self.motor:
            pos = self.motor.position
            self.position.set("{:.4f}".format(pos))

    def move_to(self, event=None):
        if self.motor:
            self.motor.move_to(float(self.move_to_val.get()))

    def move_by(self, event=None):
        if self.motor:
            self.motor.move_by(float(self.move_by_val.get()))

opened_instruments = {}

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
    # | | controls_frame    | video_frame       | properties_frame    | |
    # | |                   |                   |                     | |
    # | |                   |                   |                     | |
    # | |                   |                   |                     | |
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
        s.configure('Properties.TFrame', background='#1e1e1e', foreground='white')

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
        self.controls_frame_items.append(KCubeController(self.controls_frame, "X Stage", autogator.configurations.stage_x))
        self.controls_frame_items.append(KCubeController(self.controls_frame, "Y Stage", autogator.configurations.stage_y))
        self.controls_frame_items.append(KCubeController(self.controls_frame, "Rotation Stage", autogator.configurations.stage_deg))

        self.properties_frame = Frame(self.content_frame, width=250, borderwidth=15, style='Properties.TFrame')
        self.properties_frame.pack(side=RIGHT, fill='y', expand=False)

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

        threading.Thread(target=self.update, daemon=True).start()

    def _setup_menubar(self):
        file_menu = Menu(self.menubar, tearoff=0)
        # Maybe camera connection will be sub to file_menu?
        self.menubar.add_cascade(label="File", menu=file_menu)
        camera_menu = Menu(self.menubar, tearoff=0)
        camera_menu.add_command(label="Select camera device", command=self.select_camera)
        self.menubar.add_cascade(label="Camera", menu=camera_menu)

        edit_menu = Menu(self.menubar, tearoff=0)
        # Maybe zoom menu will be sub to edit_menu?
        self.menubar.add_cascade(label="Edit", menu=edit_menu)
        
        zoom_menu = Menu(self.menubar, tearoff=0)
        zoom_menu.add_radiobutton(label="25%", command=lambda: self.set_zoom(0.25))
        zoom_menu.add_radiobutton(label="33%", command=lambda: self.set_zoom(0.33))
        zoom_menu.add_radiobutton(label="50%", command=lambda: self.set_zoom(0.5))
        zoom_menu.add_radiobutton(label="66%", command=lambda: self.set_zoom(0.66))
        zoom_menu.add_radiobutton(label="75%", command=lambda: self.set_zoom(0.75))
        zoom_menu.add_radiobutton(label="100%", command=lambda: self.set_zoom(1.0))
        zoom_menu.add_radiobutton(label="125%", command=lambda: self.set_zoom(1.25))
        zoom_menu.add_radiobutton(label="133%", command=lambda: self.set_zoom(1.33))
        zoom_menu.add_radiobutton(label="150%", command=lambda: self.set_zoom(1.5))
        self.menubar.add_cascade(label="Zoom", menu=zoom_menu)
        
        actions_menu = Menu(self.menubar, tearoff=0)
        # Actions include snapshot, video capture, calibrate, cursor, etc.
        self.menubar.add_cascade(label="Actions", menu=actions_menu)

    def set_zoom(self, ratio):
        self.zoom_level = ratio

    def select_camera(self):
        new_camera = SelectCameraDialog(Toplevel(self.master)).selected_camera()
        if new_camera is not None:
            self.camera.stop_live_video()
            self.camera = new_camera
            self.camera.start_live_video()

    def update(self):
        while self.camera.wait_for_frame():
            self.img = self.scale_image(PIL.Image.fromarray(self.camera.latest_frame(), 'RGB'))
            self.photo = PIL.ImageTk.PhotoImage(image=self.img)
            self.canvas.create_image(0, 0, image=self.photo, anchor=NW)

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
    