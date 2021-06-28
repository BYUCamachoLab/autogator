import sys
from PyQt5.QtWidgets import QToolButton, QPushButton, QLabel, QTextEdit, QGridLayout, QApplication, QWidget
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from motion.motion import Motion


class Example(QWidget):

    def __init__(self):
        super().__init__()

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

        upContLatArrow.clicked.connect(self.upContLatButtonClicked)
        downContLatArrow.clicked.connect(self.downContLatButtonClicked)
        leftContLatArrow.clicked.connect(self.leftContLatButtonClicked)
        rightContLatArrow.clicked.connect(self.rightContLatButtonClicked)

        upJogLatArrow.clicked.connect(self.upJogLatButtonClicked)
        downJogLatArrow.clicked.connect(self.downJogLatButtonClicked)
        leftJogLatArrow.clicked.connect(self.leftJogLatButtonClicked)
        rightJogLatArrow.clicked.connect(self.rightJogLatButtonClicked)

        leftContRotArrow.clicked.connect(self.leftContRotButtonClicked)
        rightContRotArrow.clicked.connect(self.rightContRotButtonClicked)

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

    def upContLatButtonClicked(self):
        print("up cont")
    def downContLatButtonClicked(self):
        print("down cont")
    def leftContLatButtonClicked(self):
        print("left cont")
    def rightContLatButtonClicked(self):
        print("right cont")

    def upJogLatButtonClicked(self):
        print("up Jog")
    def downJogLatButtonClicked(self):
        print("down Jog")
    def leftJogLatButtonClicked(self):
        print("left Jog")
    def rightJogLatButtonClicked(self):
        print("right Jog")

    def leftContRotButtonClicked(self):
        print("left cont rot")
    def rightContRotButtonClicked(self):
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


def main():
    app = QApplication(sys.argv)
    Example()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
