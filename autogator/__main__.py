import sys

try:
    import autogator
except:
    print('USAGE: python -m autogator (did you forget "-m"?)')
    sys.exit()

print("Welcome to AutoGator, the automatic chip interrogator.")
print("(C) 2019 by Sequoia Ploeg")

import tkinter as tk
import autogator.images
import PIL.ImageTk

class Splash(tk.Toplevel):
    def __init__(self, parent):
        tk.Toplevel.__init__(self, parent)
        self.title("Splash")
        self.overrideredirect(True)
        self.geometry("400x300")
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry('{}x{}+{}+{}'.format(width, height, x, y))

        maxsize = (400, 300)
        img_holder = tk.Canvas(self, width=400, height=250)
        img_holder.pack(fill="both", expand=True)
        self.img = autogator.images.get_image_by_name('croc.jpg')
        self.img.thumbnail(maxsize)
        self.img = PIL.ImageTk.PhotoImage(self.img)
        img_holder.create_image(0, 0, image=self.img, anchor=tk.NW)

        lbl = tk.Label(self, text='AutoGator')
        lbl.pack(fill='both', expand=True)

        ## required to make window show before the program gets to the mainloop
        self.update()

class App(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.withdraw()
        splash = Splash(self)

        # Setup stuff goes here
        import time
        from autogator.ui.program import AutoGatorWindow

        window = AutoGatorWindow(self)
        self.state('zoomed')
        self.update_idletasks()
        
        # We have finished loading, so destroy splash and show window again
        splash.destroy()
        self.deiconify()
        # window.center()

if __name__ == '__main__':
    app = App()
    app.mainloop()