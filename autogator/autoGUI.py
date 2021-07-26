import sys
from PyQt5.QtWidgets import (
    QToolButton,
    QPushButton,
    QLabel,
    QTextEdit,
    QGridLayout,
    QApplication,
    QWidget,
    QComboBox,
    QFileDialog,
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
import keyboard
from PyQt5.QtCore import QTimer
import numpy as np
import autogator.dataCache as glob


class GUI(QWidget):
    def __init__(self):
        super().__init__()
        self.dataCache = glob.DataCache.get_instance()
        self.motion = self.dataCache.get_motion()
        self.circuitMap = self.dataCache.get_circuitMap()
        self.scope = self.dataCache.get_scope()
        self.dataScanner = self.dataCache.get_dataScanner()
        self.initUI()

    def initUI(self):
        upContLatArrow = QToolButton()
        upContLatArrow.setArrowType(Qt.UpArrow)
        downContLatArrow = QToolButton()
        downContLatArrow.setArrowType(Qt.DownArrow)
        leftContLatArrow = QToolButton()
        leftContLatArrow.setArrowType(Qt.LeftArrow)
        rightContLatArrow = QToolButton()
        rightContLatArrow.setArrowType(Qt.RightArrow)

        upJogLatArrow = QToolButton()
        upJogLatArrow.setArrowType(Qt.UpArrow)
        downJogLatArrow = QToolButton()
        downJogLatArrow.setArrowType(Qt.DownArrow)
        leftJogLatArrow = QToolButton()
        leftJogLatArrow.setArrowType(Qt.LeftArrow)
        rightJogLatArrow = QToolButton()
        rightJogLatArrow.setArrowType(Qt.RightArrow)

        leftContRotArrow = QToolButton()
        leftContRotArrow.setArrowType(Qt.LeftArrow)
        rightContRotArrow = QToolButton()
        rightContRotArrow.setArrowType(Qt.RightArrow)

        leftJogRotArrow = QToolButton()
        leftJogRotArrow.setArrowType(Qt.LeftArrow)
        rightJogRotArrow = QToolButton()
        rightJogRotArrow.setArrowType(Qt.RightArrow)

        upContLatArrow.pressed.connect(self.upContLatButtonPressed)
        upContLatArrow.released.connect(self.upContLatButtonReleased)
        downContLatArrow.pressed.connect(self.downContLatButtonPressed)
        downContLatArrow.released.connect(self.downContLatButtonReleased)
        leftContLatArrow.pressed.connect(self.leftContLatButtonPressed)
        leftContLatArrow.released.connect(self.leftContLatButtonReleased)
        rightContLatArrow.pressed.connect(self.rightContLatButtonPressed)
        rightContLatArrow.released.connect(self.rightContLatButtonReleased)

        upJogLatArrow.clicked.connect(self.upJogLatButtonClicked)
        downJogLatArrow.clicked.connect(self.downJogLatButtonClicked)
        leftJogLatArrow.clicked.connect(self.leftJogLatButtonClicked)
        rightJogLatArrow.clicked.connect(self.rightJogLatButtonClicked)

        leftContRotArrow.pressed.connect(self.leftContRotButtonPressed)
        leftContRotArrow.released.connect(self.leftContRotButtonReleased)
        rightContRotArrow.pressed.connect(self.rightContRotButtonPressed)
        rightContRotArrow.released.connect(self.rightContRotButtonReleased)

        leftJogRotArrow.clicked.connect(self.leftJogRotButtonClicked)
        rightJogRotArrow.clicked.connect(self.rightJogRotButtonClicked)

        self.jogSizeEditText = QTextEdit(self)
        self.jogSizeEditText.setFixedHeight(30)
        self.jogSizeEditText.setFixedWidth(100)

        # Current Jog
        self.jogSizeEditText.setText(str(self.motion.get_jog_step_linear()))
        self.jogSizeSetButton = QPushButton("Set Jog Size")
        self.jogSizeSetButton.clicked.connect(self.jogSizeSetButtonClicked)

        self.gds_x_coordinate = QTextEdit(self)
        self.gds_x_coordinate.setFixedHeight(30)
        self.gds_x_coordinate.setFixedWidth(100)

        self.gds_y_coordinate = QTextEdit(self)
        self.gds_y_coordinate.setFixedHeight(30)
        self.gds_y_coordinate.setFixedWidth(100)

        self.gdsGoToButton = QPushButton("Go")
        self.gdsGoToButton.clicked.connect(self.gdsGoToButtonClicked)

        self.x_label = QLabel("X:")
        self.y_label = QLabel("Y:")
        self.x_label2 = QLabel("X:")
        self.y_label2 = QLabel("Y:")

        self.cur_x_position_label = QLabel(str(self.motion.get_motor_position(self.motion.x_mot)))
        self.cur_y_position_label = QLabel(str(self.motion.get_motor_position(self.motion.y_mot)))

        self.timer = QTimer()
        self.timer.timeout.connect(self.printPosition)
        self.timer.start(100)

        self.circuitsMenu = QComboBox(self)
        self.circuitsMenu.setSizeAdjustPolicy(QComboBox.AdjustToContents)

        self.circuitGoToButton = QPushButton("Go")
        self.circuitGoToButton.clicked.connect(self.circuitGoToButtonClicked)

        self.loadFileButton = QPushButton("Load File")
        self.loadFileButton.clicked.connect(self.openFileNameDialog)

        self.calibrateButton = QPushButton("Re-Calibrate")
        self.calibrateButton.clicked.connect(self.calibrateSystem)

        self.auto_scan_button = QPushButton("Auto Scan")
        self.auto_scan_button.clicked.connect(self.auto_scan)

        if self.circuitMap is not None:
            self.circuits = self.circuitMap.get_circuits()
            self.circuitsMenu.clear()
            for circuit in self.circuits:
                self.circuitsMenu.addItem(circuit.ID)

        grid = QGridLayout()
        grid.setSpacing(10)

        QLabelCont = QLabel("Cont Motion")
        QLabelCont.setFont(QFont("Arial", 10))
        QLabelJog = QLabel("Jog Motion")
        QLabelJog.setFont(QFont("Arial", 10))
        QLabelLocation = QLabel("Location")
        QLabelLocation.setFont(QFont("Arial", 10))
        QLabelGoTo = QLabel("Go To")
        QLabelGoTo.setFont(QFont("Arial", 10))

        # First Column
        grid.addWidget(QLabelCont, 0, 0)
        grid.addWidget(QLabel("Lateral"), 1, 0)
        grid.addWidget(upContLatArrow, 2, 1)
        grid.addWidget(downContLatArrow, 4, 1)
        grid.addWidget(leftContLatArrow, 3, 0)
        grid.addWidget(rightContLatArrow, 3, 2)

        grid.addWidget(QLabel("Rotational"), 5, 0)
        grid.addWidget(leftContRotArrow, 6, 0)
        grid.addWidget(rightContRotArrow, 6, 2)

        grid.addWidget(QLabel(""), 8, 0)

        grid.addWidget(QLabelJog, 9, 0)
        grid.addWidget(QLabel("Lateral"), 10, 0)
        grid.addWidget(upJogLatArrow, 11, 1)
        grid.addWidget(downJogLatArrow, 13, 1)
        grid.addWidget(leftJogLatArrow, 12, 0)
        grid.addWidget(rightJogLatArrow, 12, 2)

        grid.addWidget(QLabel("Rotational"), 14, 0)
        grid.addWidget(leftJogRotArrow, 15, 0)
        grid.addWidget(rightJogRotArrow, 15, 2)

        grid.addWidget(self.jogSizeEditText, 16, 0)
        grid.addWidget(self.jogSizeSetButton, 16, 1)

        # Second Column
        grid.addWidget(QLabel(""), 0, 3)
        grid.addWidget(QLabel(""), 1, 3)

        grid.addWidget(QLabelLocation, 0, 4)

        grid.addWidget(self.x_label, 1, 4)
        grid.addWidget(self.y_label, 2, 4)

        grid.addWidget(self.cur_x_position_label, 1, 5)
        grid.addWidget(self.cur_y_position_label, 2, 5)

        grid.addWidget(QLabelGoTo, 3, 4)

        grid.addWidget(self.circuitsMenu, 5, 5)
        grid.addWidget(self.circuitGoToButton, 5, 4)
        grid.addWidget(self.loadFileButton, 4, 4)

        grid.addWidget(self.x_label2, 6, 4)
        grid.addWidget(self.y_label2, 7, 4)

        grid.addWidget(self.gds_x_coordinate, 6, 5)
        grid.addWidget(self.gds_y_coordinate, 7, 5)
        grid.addWidget(self.gdsGoToButton, 8, 4)

        grid.addWidget(self.calibrateButton, 9, 4)

        grid.addWidget(self.auto_scan_button, 10, 4)

        self.setLayout(grid)

        self.setGeometry(200, 200, 700, 400)
        self.setWindowTitle("AutoGUI")
        self.show()

    def upContLatButtonPressed(self):
        self.motion.move_cont(self.motion.y_mot, "forward")

    def upContLatButtonReleased(self):
        self.motion.stop_motion(self.motion.y_mot)

    def downContLatButtonPressed(self):
        self.motion.move_cont(self.motion.y_mot, "backward")

    def downContLatButtonReleased(self):
        self.motion.stop_motion(self.motion.y_mot)

    def leftContLatButtonPressed(self):
        self.motion.move_cont(self.motion.x_mot, "backward")

    def leftContLatButtonReleased(self):
        self.motion.stop_motion(self.motion.x_mot)

    def rightContLatButtonPressed(self):
        self.motion.move_cont(self.motion.x_mot, "forward")

    def rightContLatButtonReleased(self):
        self.motion.stop_motion(self.motion.x_mot)

    def upJogLatButtonClicked(self):
        self.motion.move_step(self.motion.y_mot, "forward")

    def downJogLatButtonClicked(self):
        self.motion.move_step(self.motion.y_mot, "backward")

    def leftJogLatButtonClicked(self):
        self.motion.move_step(self.motion.x_mot, "backward")

    def rightJogLatButtonClicked(self):
        self.motion.move_step(self.motion.x_mot, "forward")

    def leftContRotButtonPressed(self):
        self.motion.move_cont(self.motion.r_mot, "backward")

    def leftContRotButtonReleased(self):
        self.motion.stop_motion(self.motion.r_mot)

    def rightContRotButtonPressed(self):
        self.motion.move_cont(self.motion.r_mot, "forward")

    def rightContRotButtonReleased(self):
        self.motion.stop_motion(self.motion.r_mot)

    def leftJogRotButtonClicked(self):
        self.motion.move_step(self.motion.r_mot, "backward")

    def rightJogRotButtonClicked(self):
        self.motion.move_step(self.motion.r_mot, "forward")

    def jogSizeSetButtonClicked(self):
        if check_float(self.jogSizeEditText.toPlainText()):
            new_jog_size = float(self.jogSizeEditText.toPlainText())
            if new_jog_size < 2 and new_jog_size > 0.00001:
                self.motion.set_jog_step_linear(new_jog_size)
        print(self.jogSizeEditText.toPlainText())
        print("Jog size set to ^")

    def gdsGoToButtonClicked(self):
        self.motion.go_to_gds_coordinates(
            float(self.gds_x_coordinate.toPlainText()),
            float(self.gds_y_coordinate.toPlainText()),
        )

    def circuitGoToButtonClicked(self):
        if self.circuitsMenu.currentText() != "":
            locationToGo = self.circuitMap.get_circuit(
                "ID", self.circuitsMenu.currentText()
            ).location
            self.motion.go_to_gds_coordinates(
                float(locationToGo[0]), float(locationToGo[1])
            )

    def printPosition(self):
        if self.motion.conversion_matrix is not None:
            stage_pos = np.array(
                [
                    [self.motion.get_motor_position(self.motion.x_mot)],
                    [self.motion.get_motor_position(self.motion.y_mot)],
                    [1],
                ]
            )
            newPoint = np.linalg.inv(self.motion.conversion_matrix) @ stage_pos
            self.cur_x_position_label.setText(str(newPoint[0][0]))
            self.cur_y_position_label.setText(str(newPoint[1][0]))

    def openFileNameDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(
            self,
            "QFileDialog.getOpenFileName()",
            "",
            "All Files (*);;Text Files (*.txt)",
            options=options,
        )
        if fileName:
            self.dataCache.set_circuitMap_path(fileName)
            self.circuitMap = self.dataCache.get_circuitMap()
            self.circuits = self.circuitMap.get_circuits()
            self.circuitsMenu.clear()
            for circuit in self.circuits:
                self.circuitsMenu.addItem(circuit.ID)

    def calibrateSystem(self):
        # self.data_cache.calibrate()
        pass

    def auto_scan(self):
        self.dataScanner.auto_scan()


def check_float(potential_float):
    try:
        float(potential_float)
        return True
    except ValueError:
        return False


def Start():
    m = GUI()
    m.show()
    return m


def main():
    app = QApplication(sys.argv)
    window = Start()
    app.exec_()


if __name__ == "__main__":
    main()
