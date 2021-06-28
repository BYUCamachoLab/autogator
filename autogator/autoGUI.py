import sys
import PyQt5
from PyQt5.QtWidgets import QToolButton, QPushButton, QLabel, QTextEdit, QGridLayout, QApplication, QWidget
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from motion.motion import Motion


class Example(QWidget):

    def __init__(self):
        super().__init__()

        self.initUI()
        self.motion = Motion()

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
        #Current Jog
        self.jogSizeEditText.setText("current jog")
        jogSizeSetButton = QPushButton("Set Jog Size")
        jogSizeSetButton.clicked.connect(self.jogSizeSetButtonClicked)

        self.velocityEditText = QTextEdit(self)
        self.velocityEditText.setFixedHeight(30)
        self.velocityEditText.setFixedWidth(100)
        #Current Velocity
        self.velocityEditText.setText("current velocity")
        velocitySetButton = QPushButton("Set Velocity")
        velocitySetButton.clicked.connect(self.velocitySetButtonClicked)

        grid = QGridLayout()
        grid.setSpacing(10)

        QLabelCont = QLabel("Cont Motion")
        QLabelCont.setFont(QFont('Arial', 10))
        QLabelJog = QLabel("Jog Motion")
        QLabelJog.setFont(QFont('Arial', 10))



        grid.addWidget(QLabelCont, 0, 0)
        grid.addWidget(QLabel("Lateral"), 1, 0)
        grid.addWidget(upContLatArrow, 2, 1)
        grid.addWidget(downContLatArrow, 4, 1)
        grid.addWidget(leftContLatArrow, 3, 0)
        grid.addWidget(rightContLatArrow, 3, 2)

        grid.addWidget(QLabel("Rotational"), 5, 0)
        grid.addWidget(leftContRotArrow, 6, 0)
        grid.addWidget(rightContRotArrow, 6, 2)

        grid.addWidget(self.velocityEditText, 7, 0)
        grid.addWidget(velocitySetButton, 7, 1)

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
        grid.addWidget(jogSizeSetButton, 16, 1)

        self.setLayout(grid)

        self.setGeometry(300, 300, 300, 300)
        self.setWindowTitle('Review')
        self.show()

    def upContLatButtonPressed(self):
        print("up cont go")
    def upContLatButtonReleased(self):
        print("up cont stop")
    def downContLatButtonPressed(self):
        print("down cont go")
    def downContLatButtonReleased(self):
        print("down cont stop")
    def leftContLatButtonPressed(self):
        print("left cont go")
    def leftContLatButtonReleased(self):
        print("left cont stop")
    def rightContLatButtonPressed(self):
        print("right cont go")
    def rightContLatButtonReleased(self):
        print("right cont stop")


    def upJogLatButtonClicked(self):
        print("up Jog")
    def downJogLatButtonClicked(self):
        print("down Jog")
    def leftJogLatButtonClicked(self):
        print("left Jog")
    def rightJogLatButtonClicked(self):
        print("right Jog")

    def leftContRotButtonPressed(self):
        print("left cont rot")
    def leftContRotButtonReleased(self):
        print("left cont rot")
    def rightContRotButtonPressed(self):
        print("right cont rot")
    def rightContRotButtonReleased(self):
        print("right cont rot")

    def leftJogRotButtonClicked(self):
        print("left Jog rot")
    def rightJogRotButtonClicked(self):
        print("right Jog rot")

    def jogSizeSetButtonClicked(self):
        print(self.jogSizeEditText.toPlainText())
        print("Jog size set to ^")

    def velocitySetButtonClicked(self):
        print(self.velocityEditText.toPlainText())
        print("Velocity set to ^")


def Start():
    m = Example()
    m.show()
    return m

def main():
    app = QApplication(sys.argv)
    window = Start()
    app.exec_()


if __name__ == '__main__':
    main()
