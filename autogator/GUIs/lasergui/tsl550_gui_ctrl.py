import sys
from functools import partial
import time
from numpy import log10

from PyQt5.QtWidgets import (
    QApplication, QDialog, QMainWindow, QMessageBox, QWidget
)
from PyQt5.QtCore import QThreadPool

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
        self.thread_manager = QThreadPool()
        #Connect to laser
        ns = locate_ns(NAME_SERVER)
        self.laser = Proxy(ns.lookup(LASER_NAME))
        print(self.laser.autoconnect())
        self.setupLaser()
        self.connectSignalsSlots()
        self.changeWFVal = True # Flag used to make sure won't change the wavelength/frequency when we switch between the two
        self.changePVal = True #Flag used so we don't change the power value when we switch betwen dB and mW
        self.currentThread = True #Flag used to specify if the which thread has control of the laser
        
    
    def __del__(self):
        # Clean up the laser
        self.laser.close()
        # pass


    def setupLaser(self):
        laser_status = self.laser.status()
        if laser_status[0]=='-':
            self.LaserDiode.setChecked(True)
        #Start with the shutter closed and minimal power so we don't destroy anything by accident
        self.laser.close_shutter()
        self.Shutter.setChecked(False)
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
        self.LaserDiode.s#FIXME Test this with the actual laser
        self.PowerValue.setDisabled(disable)
        self.WavFreqVal.setDisabled(disable)
        self.PowerLabel.setDisabled(disable)
        self.WavFreqLabel.setDisabled(disable)
        self.LaserDiode.setDisabled(disable)
        self.Shutter.setDisabled(disable)
        self.ChangeDigitButton.setDisabled(disable)
        print("function was called")


    def selectDigit(self, newSize):
        #used in connection with changeDigit() (we need it to make the functionality work)
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
        #Just something include what the GUI is about
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
            "<p>Instructions<\p>"
            "<p>- Click on \"Change Digit\" to select which digit you want to change<\p>"
            "<p>- Toggle between dB and mW, wavelength and frequency using drop-down boxes<\p>"
            "<p>- Use check boxes to open/close shutter and turn the laser diode on/off<\p>"
        )


    def waitForLD(self):
        #Tells the user that the Laser Diode is warming up, and that the
        #GUI will be re-enabled once it is on
        QMessageBox.about(
            self,
            "Wait!",
            "<p>Wait for the Laser Diode to turn on.<\p>"
            "<p>The GUI will be re-enabled once the Laser Diode is fully on.<\p>"
        )
    

    def mWtodB(self, power_mW):
        return 10*log10(power_mW)
    

    def dBtomW(self, power_dB):
        print(power_dB)
        num = 10**(power_dB/10)
        print(num)
        return num


    def swapWavFreq(self):
        # Check if the laser is on this thread; it is not, claim it
        if not self.currentThread:
            self.laser._pyroClaimOwnership()
            self.currentThread = True

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
        # Check if the laser is on this thread; it is not, claim it
        if not self.currentThread:
            self.laser._pyroClaimOwnership()
            self.currentThread = True

        self.changePVal = False
        if self.PowerLabel.currentIndex()==0:
            #Power label is changed to dB
            self.PowerValue.setMinimum(-10.00)
            self.PowerValue.setMaximum(16.98)
            self.PowerValue.setValue(self.mWtodB(self.PowerValue.value()) if not self.Shutter.isChecked() else self.laser.power_dBm())
            #see notes above in swapValFreq function
        else:
            #Power label is changed to mW
            #see notes above in swapValFreq function
            self.PowerValue.setValue(self.dBtomW(self.PowerValue.value()) if not self.Shutter.isChecked() else self.laser.power_mW())
            self.PowerValue.setMinimum(0.1)
            self.PowerValue.setMaximum(30)
            

    def changeWavFreqVal(self):
        # Check if the laser is on this thread; it is not, claim it
        if not self.currentThread:
            self.laser._pyroClaimOwnership()
            self.currentThread = True
        
        # If the unit (wavelength or frequency) was changed, don't do anything; just return and reset the flag
        if not self.changeWFVal:
            self.changeWFVal = True
            print("Changed the change value")
            return

        #call appropriate laser functions
        if self.WavFreqLabel.currentIndex()==0:
            print("Wavelength changed")
            self.laser.wavelength(self.WavFreqVal.value())
            print(self.laser.wavelength())
        else:
            print("Frequency changed")
            self.laser.frequency(self.WavFreqVal.value())
            print(self.laser.frequency())
    

    def changePowerVal(self):
        # Check if the laser is on this thread; it is not, claim it
        if not self.currentThread:
            self.laser._pyroClaimOwnership()
            self.currentThread = True
        
        # If the unit (dB or mW) was changed, don't do anything; just return and reset the flag
        if not self.changePVal:
            self.changePVal = True
            print("changed the Power change value")
            return
        
        # Call laser funcions to change power
        if self.PowerLabel.currentIndex()==0:
            print("dB changed")
            self.laser.power_dBm(self.PowerValue.value())
            print(self.laser.power_dBm())
        else:
            print("mW changed")
            self.laser.power_mW(self.PowerValue.value())
            print(self.laser.power_mW())
    

    def openCloseShutter(self):
        # Check if the laser is on this thread; it is not, claim it
        if not self.currentThread:
            self.laser._pyroClaimOwnership()
            self.currentThread = True
        
        if self.Shutter.isChecked():
            print("Open shutter")
            self.laser.open_shutter()
        else:
            print("Close shutter")
            self.laser.close_shutter()
        

    def LDswitch(self):
        # Check if the laser is on this thread; it is not, claim it
        if not self.currentThread:
            self.laser._pyroClaimOwnership()
            self.currentThread = True
        
        #disable the widgets, turn on the laser, set the thread flag
        if self.LaserDiode.isChecked():
            print("LD is on")
            self.disableAllWidgets(True)
            self.waitForLD()
            self.currentThread = False
            self.laser.on()
            self.thread_manager.start(self.WaitLDOn)
        else:
            print("Ld is off")
            self.laser.off()

    #Function that waits until the Laser Diode has turned on; operates on a new thread
    def WaitLDOn(self):
        while True:
            time.sleep(1)
            #This takes ownership of the laser so that this thread can access its functions
            #Ownership has to be regiven to the main thread later
            self.laser._pyroClaimOwnership()
            status = self.laser.status()
            print(status)
            if status[0]=='-':
                break
            
        self.disableAllWidgets(False)

        
    

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