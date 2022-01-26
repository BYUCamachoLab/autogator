# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'window_main.ui'
##
## Created by: Qt User Interface Compiler version 5.15.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import (
    QCoreApplication,
    QDate,
    QDateTime,
    QMetaObject,
    QObject,
    QPoint,
    QRect,
    QSize,
    QTime,
    QUrl,
    Qt,
)
from PySide2.QtGui import (
    QBrush,
    QColor,
    QConicalGradient,
    QCursor,
    QFont,
    QFontDatabase,
    QIcon,
    QKeySequence,
    QLinearGradient,
    QPalette,
    QPainter,
    QPixmap,
    QRadialGradient,
)
from PySide2.QtWidgets import *

from . import res_rc


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(800, 600)
        icon = QIcon()
        icon.addFile(
            u":/images/images/favicon-32x32.png", QSize(), QIcon.Normal, QIcon.Off
        )
        MainWindow.setWindowIcon(icon)
        MainWindow.setStyleSheet(u"")
        self.actionAdd_Device = QAction(MainWindow)
        self.actionAdd_Device.setObjectName(u"actionAdd_Device")
        self.actionAdd_Device.setIcon(icon)
        self.actionSelect_camera = QAction(MainWindow)
        self.actionSelect_camera.setObjectName(u"actionSelect_camera")
        self.actionAdd_ThorLabs_devices = QAction(MainWindow)
        self.actionAdd_ThorLabs_devices.setObjectName(u"actionAdd_ThorLabs_devices")
        self.action25 = QAction(MainWindow)
        self.action25.setObjectName(u"action25")
        self.action33 = QAction(MainWindow)
        self.action33.setObjectName(u"action33")
        self.action50 = QAction(MainWindow)
        self.action50.setObjectName(u"action50")
        self.action66 = QAction(MainWindow)
        self.action66.setObjectName(u"action66")
        self.action75 = QAction(MainWindow)
        self.action75.setObjectName(u"action75")
        self.action100 = QAction(MainWindow)
        self.action100.setObjectName(u"action100")
        self.action125 = QAction(MainWindow)
        self.action125.setObjectName(u"action125")
        self.action133 = QAction(MainWindow)
        self.action133.setObjectName(u"action133")
        self.action150 = QAction(MainWindow)
        self.action150.setObjectName(u"action150")
        self.actionExit = QAction(MainWindow)
        self.actionExit.setObjectName(u"actionExit")
        self.actionLocate_DLL = QAction(MainWindow)
        self.actionLocate_DLL.setObjectName(u"actionLocate_DLL")
        self.actionStop_All = QAction(MainWindow)
        self.actionStop_All.setObjectName(u"actionStop_All")
        icon1 = QIcon()
        icon1.addFile(u":/images/images/stop.jpg", QSize(), QIcon.Normal, QIcon.Off)
        self.actionStop_All.setIcon(icon1)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.centralwidget.setLayoutDirection(Qt.LeftToRight)
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.frame_Controllers = QFrame(self.centralwidget)
        self.frame_Controllers.setObjectName(u"frame_Controllers")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.frame_Controllers.sizePolicy().hasHeightForWidth()
        )
        self.frame_Controllers.setSizePolicy(sizePolicy)
        self.frame_Controllers.setBaseSize(QSize(200, 0))
        self.frame_Controllers.setFrameShape(QFrame.NoFrame)
        self.frame_Controllers.setFrameShadow(QFrame.Raised)
        self.verticalLayout = QVBoxLayout(self.frame_Controllers)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.listView_Controllers = QListView(self.frame_Controllers)
        self.listView_Controllers.setObjectName(u"listView_Controllers")
        self.listView_Controllers.setMinimumSize(QSize(200, 0))

        self.verticalLayout.addWidget(self.listView_Controllers)

        self.horizontalLayout.addWidget(self.frame_Controllers)

        self.frame_CameraDisplay = QFrame(self.centralwidget)
        self.frame_CameraDisplay.setObjectName(u"frame_CameraDisplay")
        sizePolicy1 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy1.setHorizontalStretch(2)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(
            self.frame_CameraDisplay.sizePolicy().hasHeightForWidth()
        )
        self.frame_CameraDisplay.setSizePolicy(sizePolicy1)
        self.frame_CameraDisplay.setFrameShape(QFrame.NoFrame)
        self.frame_CameraDisplay.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_2 = QHBoxLayout(self.frame_CameraDisplay)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.graphicsView_Screen = QGraphicsView(self.frame_CameraDisplay)
        self.graphicsView_Screen.setObjectName(u"graphicsView_Screen")

        self.horizontalLayout_2.addWidget(self.graphicsView_Screen)

        self.horizontalLayout.addWidget(self.frame_CameraDisplay)

        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 800, 22))
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName(u"menuFile")
        self.menuDevices = QMenu(self.menubar)
        self.menuDevices.setObjectName(u"menuDevices")
        self.menuZoom_level = QMenu(self.menuDevices)
        self.menuZoom_level.setObjectName(u"menuZoom_level")
        self.menuMotors = QMenu(self.menubar)
        self.menuMotors.setObjectName(u"menuMotors")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.toolBar = QToolBar(MainWindow)
        self.toolBar.setObjectName(u"toolBar")
        self.toolBar.setMovable(False)
        MainWindow.addToolBar(Qt.TopToolBarArea, self.toolBar)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuDevices.menuAction())
        self.menubar.addAction(self.menuMotors.menuAction())
        self.menuFile.addAction(self.actionExit)
        self.menuDevices.addAction(self.actionSelect_camera)
        self.menuDevices.addSeparator()
        self.menuDevices.addAction(self.menuZoom_level.menuAction())
        self.menuZoom_level.addAction(self.action25)
        self.menuZoom_level.addAction(self.action33)
        self.menuZoom_level.addAction(self.action50)
        self.menuZoom_level.addAction(self.action66)
        self.menuZoom_level.addAction(self.action75)
        self.menuZoom_level.addAction(self.action100)
        self.menuZoom_level.addAction(self.action125)
        self.menuZoom_level.addAction(self.action133)
        self.menuZoom_level.addAction(self.action150)
        self.menuMotors.addAction(self.actionLocate_DLL)
        self.menuMotors.addAction(self.actionAdd_ThorLabs_devices)
        self.toolBar.addAction(self.actionAdd_Device)
        self.toolBar.addAction(self.actionStop_All)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)

    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(
            QCoreApplication.translate("MainWindow", u"Autogator", None)
        )
        self.actionAdd_Device.setText(
            QCoreApplication.translate("MainWindow", u"Add Device", None)
        )
        self.actionSelect_camera.setText(
            QCoreApplication.translate("MainWindow", u"Select camera", None)
        )
        self.actionAdd_ThorLabs_devices.setText(
            QCoreApplication.translate("MainWindow", u"Open ThorLabs devices", None)
        )
        self.action25.setText(QCoreApplication.translate("MainWindow", u"25%", None))
        self.action33.setText(QCoreApplication.translate("MainWindow", u"33%", None))
        self.action50.setText(QCoreApplication.translate("MainWindow", u"50%", None))
        self.action66.setText(QCoreApplication.translate("MainWindow", u"66%", None))
        self.action75.setText(QCoreApplication.translate("MainWindow", u"75%", None))
        self.action100.setText(QCoreApplication.translate("MainWindow", u"100%", None))
        self.action125.setText(QCoreApplication.translate("MainWindow", u"125%", None))
        self.action133.setText(QCoreApplication.translate("MainWindow", u"133%", None))
        self.action150.setText(QCoreApplication.translate("MainWindow", u"150%", None))
        self.actionExit.setText(QCoreApplication.translate("MainWindow", u"Exit", None))
        self.actionLocate_DLL.setText(
            QCoreApplication.translate("MainWindow", u"Locate ThorLabs DLLs", None)
        )
        self.actionStop_All.setText(
            QCoreApplication.translate("MainWindow", u"Stop All", None)
        )
        # if QT_CONFIG(tooltip)
        self.actionStop_All.setToolTip(
            QCoreApplication.translate(
                "MainWindow", u"Immediately stop all motion", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", u"File", None))
        self.menuDevices.setTitle(
            QCoreApplication.translate("MainWindow", u"Camera", None)
        )
        self.menuZoom_level.setTitle(
            QCoreApplication.translate("MainWindow", u"Zoom level", None)
        )
        self.menuMotors.setTitle(
            QCoreApplication.translate("MainWindow", u"Motors", None)
        )
        self.toolBar.setWindowTitle(
            QCoreApplication.translate("MainWindow", u"toolBar", None)
        )

    # retranslateUi
