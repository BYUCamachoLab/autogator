import sys
from functools import partial
import time

from PyQt5.QtWidgets import (
    QApplication, QDialog, QMainWindow, QMessageBox, QWidget
)

from tsl550_ui import Ui_MainWindow
from change_digit_ui import Ui_ChangeDigit

from pyrolab.api import locate_ns, Proxy



__version__ = '0.1'
__author__ = 'Benjamin Arnesen'

NAME_SERVER = "camacholab.ee.byu.edu"
LASER_NAME = "westview.scarletwitch"



class tsl550Ui(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setFixedSize(480, 180)
        self.step_size = 1
        #Connect to laser
        ns = locate_ns(NAME_SERVER)
        self.laser = Proxy(ns.lookup(LASER_NAME))
        print(self.laser.autoconnect())
        self.setupLaser()
        self.connectSignalsSlots()
        self.changeWFVal = True
        self.changePVal = True
        self.saveus = True
        

    
    def __del__(self):
        self.laser.close()

    def setupLaser(self):
        laser_status = self.laser.status()
        if laser_status[0]=='-':
            self.LaserDiode.setChecked(True)
        self.laser.close_shutter()
        self.Shutter.setChecked(False) #check to make sure these two are working
        self.laser.wavelength(1550)
        self.laser.power_dBm(-10.00)
        self.PowerValue.setValue(-10.00)
        
    
    def connectSignalsSlots(self):
        self.actionAbout.triggered.connect(self.about)
        self.actionInstructions.triggered.connect(self.instructions)
        self.action_Change_Digit.triggered.connect(self.changeDigit)
        self.ChangeDigitButton.clicked.connect(self.changeDigit)
        self.WavFreqLabel.currentIndexChanged.connect(self.swapWavFreq)
        self.PowerLabel.currentIndexChanged.connect(self.swapPower)
        self.WavFreqVal.valueChanged.connect(self.changeWavFreqVal)
        self.PowerValue.valueChanged.connect(self.changePowerVal)
        self.Shutter.stateChanged.connect(self.openCloseShutter)
        # self.LaserDiode.stateChanged.connect(self.disableAllWidgets)
        self.LaserDiode.stateChanged.connect(self.LDswitch)
        # self.ExtraButton.clicked.connect(self.extraFunction)

    def extraFunction(self):
        self.disableAllWidgets(self.saveus)
        self.saveus = not self.saveus

    def disableAllWidgets(self, disable):
        # disable = self.LaserDiode.isChecked()
        print(disable)
        self.PowerValue.setDisabled(disable)
        self.WavFreqVal.setDisabled(disable)
        self.PowerLabel.setDisabled(disable)
        self.WavFreqLabel.setDisabled(disable)
        # self.LaserDiode.setDisabled(disable) #this one?
        self.Shutter.setDisabled(disable)
        print("function was called")
        self.LDswitch()

    def selectDigit(self, newSize):
        self.step_size = newSize

    def changeDigit(self):
        dialog = ChangeDigitDialog()
        #Save which digit wants to be changed in step_size 
        dialog.comboBox.currentIndexChanged.connect(dialog.changeTargetVal)
        dialog.Hundreds.clicked.connect(partial(self.selectDigit,100))
        dialog.Tens.clicked.connect(partial(self.selectDigit,10))
        dialog.Ones.clicked.connect(partial(self.selectDigit,1))
        dialog.Tenths.clicked.connect(partial(self.selectDigit,0.1))
        dialog.Hundredths.clicked.connect(partial(self.selectDigit,0.01))
        dialog.Thousandths.clicked.connect(partial(self.selectDigit,0.001))
        dialog.TensOfThousandths.clicked.connect(partial(self.selectDigit,0.0001))

        #If the "Okay" button is selected on the dialog, change the step size accordingly
        #Don't change anything if the "Cancel" button is selected
        if dialog.exec()==1:
            if not dialog.change_power:
                self.WavFreqVal.setSingleStep(self.step_size)
            elif dialog.change_power and self.step_size > 0.001:
                self.PowerValue.setSingleStep(self.step_size)
    
    def about(self):
        QMessageBox.about(
            self,
            "TSL550 GUI",
            "<p>GUI for the TSL550 laser<\p>"
            "<p>Built as part of autogator"
        )

    def instructions(self):
        #Function to disply how to use the GUI
        QMessageBox.about(
            self,
            "Instructions",
            "<p>- Click on \"Change Digit\" to select which digit you want to change<\p>"
            "<p>- Toggle between dB and mW, wavelength and frequency using drop-down boxes<\p>"
            "<p>- Use check boxes to open/close shutter and turn the laser diode on/off<\p>"
        )

    def swapWavFreq(self):
        self.changeWFVal = False
        if self.WavFreqLabel.currentIndex()==0:
            #this means it changed to being in terms of wavelength
            self.WavFreqVal.setMinimum(1500.0)
            self.WavFreqVal.setMaximum(1630.0)
            self.WavFreqVal.setDecimals(4)
            self.WavFreqVal.setValue(self.laser.wavelength())
            print("Changed to wavelength")
            #get the wavelength value from the laser; or just convert it using a converter?
                #is there a funcion for this? or should I write one? if I write one, confirm it with the laser downstairs
            # print("Current index is 0")
        else:
            #This means the label changed to being in terms of frequency
            self.WavFreqVal.setMinimum(183.92175)
            self.WavFreqVal.setMaximum(199.86163)
            self.WavFreqVal.setDecimals(5)
            self.WavFreqVal.setValue(self.laser.frequency())
            print("Changed to frequency")
            #see notes above
            # print("Current index is 1")

    def swapPower(self):
        self.changePVal = False
        if self.PowerLabel.currentIndex()==0:
            #Power label is changed to dB
            self.PowerValue.setMinimum(-10.00)
            self.PowerValue.setMaximum(16.98)
            self.PowerValue.setValue(self.laser.power_dBm())
            #see notes above in swapValFreq function
            # print("Current index is 0")
        else:
            #Power label is changed to mW
            # #see notes above in swapValFreq function
            self.PowerValue.setMinimum(0.1)
            self.PowerValue.setMaximum(30)
            self.PowerValue.setValue(self.laser.power_mW())
            # print("Current index is 1")

    def changeWavFreqVal(self):
        if not self.changeWFVal:
            self.changeWFVal = True
            print("Changed the change value")
            return

        #call appropriate laser functions
        if self.WavFreqLabel.currentIndex()==0:
            print("Wavelength changed")
            self.laser.wavelength(self.WavFreqVal.value())
            # self.changeWFVal = False
            # self.WavFreqVal.setValue(self.laser.wavelength())
            # just trust that this is the right value??? or do the thread thing
            print(self.laser.wavelength())
        else:
            print("Frequency changed")
            self.laser.frequency(self.WavFreqVal.value())
            print(self.laser.frequency())
    
    def changePowerVal(self):
        if not self.changePVal:
            self.changePVal = True
            print("changed the Power change value")
            return
        
        if self.PowerLabel.currentIndex()==0:
            print("dB changed")
            self.laser.power_dBm(self.PowerValue.value())
            # time.sleep(0.01)
            print(self.laser.power_dBm())
        else:
            print("mW changed")
            self.laser.power_mW(self.PowerValue.value())
            # time.sleep(0.01)
            print(self.laser.power_mW())
    
    def openCloseShutter(self):
        if self.Shutter.isChecked():
            print("Open shutter")
            self.laser.open_shutter()
        else:
            print("Close shutter")
            self.laser.close_shutter()
        
    def LDswitch(self):
        
        if self.LaserDiode.isChecked():
            print("LD is on")
            # self.disableAllWidgets(True)
            #FIXME this function ain't workin'
            self.laser.on()
            while True:
                time.sleep(1)
                status = self.laser.status()
                print(status)
                if status[0]=='-':
                    break
            # self.disableAllWidgets(False)
        else:
            print("Ld is off")
            self.laser.off()


        
    

class ChangeDigitDialog(QDialog, Ui_ChangeDigit):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.change_power = 0
    
    def changeTargetVal(self, newVal):
        self.change_power = newVal
    
    

    
    


def main():
    tsl550gui = QApplication(sys.argv)
    veiw = tsl550Ui()
    veiw.show()
    sys.exit(tsl550gui.exec_())

if __name__ == "__main__":
    main()