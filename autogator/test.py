import sys
import threading

from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QKeySequence, QShortcut
from pydantic import BaseSettings

from autogator.autogator.hardware import Stage


loader = QUiLoader()

class KeyboardGUIBindings(BaseSettings):
    '''
    Sets default keyboard bindings for KeyboardControlGUI controller.

    Because settings are implemented using Pydantic, environmental variables
    can be used to override the default settings.

    Motor axis must begin with "POS" or "MINUS" and be separated by a underscore and then the 
    motor axis
    '''
    POS_Y: str = 'w'
    MINUS_Y: str = 's'
    POS_X: str = 'd'
    MINUS_X: str = 'a'
    POS_Z: str = 'e'
    MINUS_Z: str = 'q'
    POS_PSI: str = 'c'
    MINUS_PSI: str = 'z'
    HOME: str = 'h'

class KeyboardControlGUI:
    '''
    A GUI version of the keyboard controller.
    '''

    def __init__(self, stage: Stage, bindings: KeyboardBindings = None):
        if bindings is None:
            bindings = KeyboardBindings()
        self.bindings = bindings

        self.axes = {
            'X': threading.Semaphore(), 
            'Y': threading.Semaphore(),
            'Z': threading.Semaphore(), 
            'PSI': threading.Semaphore()
        }
        self.app = QtWidgets.QApplication(sys.argv)
        self.w = loader.load('keyboardGUI.ui', None)

        self.bindingPairs = self._mapBindings(bindings)
        self.mainWindowSetup()
        
    def run(self):
        self.w.show()
        self.app.exec_()
    
    def _mapBindings(self, bindings):
        bindingNames = [attr for attr in dir(bindings) if not attr.startswith('_') and attr.isupper() and '_' in attr]
        buttons = self.w.motionControls.buttons()
        bindingTups = []
        for button in buttons:
            for binding in bindingNames:
                if button.objectName() == binding:
                    bindingTups.append((button, binding))

        if len(bindingTups) != len(self.axes.keys())*2:
            raise RuntimeError('Number of bindings doesn\'t match the number of motion buttons.')
        return bindingTups

    def _moveEvent(self, button):
        buttonName = button.objectName()
        # Get the axis of direction
        axis = None
        for axis in self.axes.keys(): 
            if axis in buttonName:
                axis = eval(f'self.stage.{axis.lower()}')
                break

        # Get the direction of the button
        direction = 'forward'
        if 'MINUS' in buttonName:
            direction = 'backward'

        # See if we need to move continuous or not
        semaphore = self.axes[axis]
        if semaphore.acquire(timeout=0.1):
            if self.w.stepRadio.isChecked():
                motionValue = self.w.stepSpinBox.value()
                axis.move_by(motionValue)
                semaphore.release()
            else:
                motionValue = self.w.velocitySpinBox.value()
                axis.move_cont(direction)
                axis.stop()
                semaphore.release()

    def mainWindowSetup(self):
        self.w.setWindowTitle('Keyboard Control')
        self.w.continuousRadio.setChecked(True)

        # Setup motion controls
        for button, bindingName in self.bindingPairs:
            binding = getattr(self.bindings, bindingName)
            self._setupButton(binding, button, self._moveEvent)

    def _setupButton(self, key, button, function):
        shortcut = QShortcut(QKeySequence(key), self.w)
        shortcut.activated.connect(button.pressed)
        button.clicked.connect(lambda checked=True, b=button: function(b))


if __name__ == '__main__':
    from autogator.api import load_default_configuration
    config = load_default_configuration()
    stage = config.get_stage()

    keyboardObj = KeyboardControlGUI(stage)
    keyboardObj.run()
    #TODO run this and debug from there
