import sys

try:
    import autogator
except:
    print('USAGE: python -m autogator (did you forget "-m"?)')
    sys.exit()

print("Welcome to AutoGator, the automatic chip interrogator.")
print("(C) 2019 by Sequoia Ploeg")

import os
import tkinter as tk

from autogator.ui.launcher import Launcher

if __name__ == '__main__':
    app = tk.Tk()
    window = Launcher(app)
    app.mainloop()