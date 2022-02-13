# -*- coding: utf-8 -*-
#
# Copyright © Autogator Project Contributors
# Licensed under the terms of the GNU GPLv3+ License
# (see autogator/__init__.py for details)

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Form(QDialog):
    """Just a simple dialog with a couple of widgets"""

    def __init__(self, parent=None):
        super(Form, self).__init__(parent)
        self.browser = QTextBrowser()
        self.setWindowTitle("Just a dialog")
        self.lineedit = QLineEdit("Write something and press Enter")
        self.lineedit.selectAll()
        layout = QVBoxLayout()
        layout.addWidget(self.browser)
        layout.addWidget(self.lineedit)
        self.setLayout(layout)
        self.lineedit.setFocus()
        self.connect(self.lineedit, SIGNAL("returnPressed()"), self.update_ui)

    def update_ui(self):
        self.browser.append(self.lineedit.text())


def start_gui():
    import sys, time

    app = QApplication()

    # Create and display the splash screen
    splash_pix = QPixmap("autogator/resources/images/croc.jpg")

    splash = QSplashScreen(splash_pix)
    splash.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
    splash.setEnabled(False)

    # adding progress bar
    progressBar = QProgressBar(splash)
    progressBar.setMaximum(10)
    progressBar.setGeometry(0, splash_pix.height() - 50, splash_pix.width(), 20)

    splash.show()
    splash.showMessage(
        "<h1><font color='green'>Welcome BeeMan!</font></h1>",
        Qt.AlignTop | Qt.AlignCenter,
        Qt.black,
    )

    for i in range(1, 11):
        progressBar.setValue(i)
        t = time.time()
        while time.time() < t + 0.1:
            app.processEvents()

    # Simulate something that takes time
    time.sleep(1)

    form = Form()
    form.show()
    splash.finish(form)
    sys.exit(app.exec_())
