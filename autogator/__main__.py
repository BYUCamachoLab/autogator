# -*- coding: utf-8 -*-
#
# Copyright © Autogator Project Contributors
# Licensed under the terms of the MIT License
# (see autogator/__init__.py for details)

from datetime import date
import configparser
import atexit

from autogator.mainwindow import start_gui


def onstart():
    from autogator.controllers.startup import startup
    startup()

@atexit.register
def onclose():
    from autogator.controllers.shutdown import shutdown
    shutdown()
    

if __name__ == "__main__":
    print("Welcome to Autogator!")
    print("© 2019-{}, CamachoLab".format(date.today().year))
    onstart()

    start_gui()
