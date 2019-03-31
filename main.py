import sys

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import (QApplication, QInputDialog, QLineEdit,
                             QMainWindow, QPushButton, QWidget)

from lib import Single_inverted_pendulum
from res import Ui_Dialog


class Unite():
    def __init__(self, ui):
        self.ui = ui
        self.reseted = True
        self.pressed = False
        self.ctrl = Single_inverted_pendulum()

    def get_M(self):
        return eval(self.ui.lineEdit.text())

    def get_m(self):
        return eval(self.ui.lineEdit_2.text())

    def get_L(self):
        return eval(self.ui.lineEdit_3.text())

    def get_u(self):
        return eval(self.ui.lineEdit_4.text())

    def get_P(self):
        return eval(self.ui.lineEdit_5.text())

    def get_I(self):
        return eval(self.ui.lineEdit_6.text())

    def get_D(self):
        return eval(self.ui.lineEdit_7.text())

    def reset(self):
        self.reseted = True
        ui.pushButton.setText("   开始")
        self.ui.lineEdit.setText("0.5")
        self.ui.lineEdit_2.setText("0.2")
        self.ui.lineEdit_3.setText("0.6")
        self.ui.lineEdit_4.setText("0.1")
        self.ui.lineEdit_5.setText("100")
        self.ui.lineEdit_6.setText("1")
        self.ui.lineEdit_7.setText("30")

    def firstButton(self):
        if self.reseted:
            return self.__start()
        elif self.pressed:
            return self.__pause()
        else:
            return self.__continue()

    def __start(self):
        self.reseted = False
        self.pressed = True
        self.ctrl.set(
            mCart=self.get_M(),
            mPend=self.get_m(),
            L=self.get_L(),
            b=self.get_u(),
            Kp=self.get_P(),
            Ki=self.get_I(),
            Kd=self.get_D())

        print("start")
        ui.pushButton.setText("   暂停")

    def __pause(self):
        self.pressed = False

        print("pause")
        ui.pushButton.setText("   继续")

    def __continue(self):
        self.pressed = True

        print("continue")
        ui.pushButton.setText("   暂停")

    def drawInit(self):
        grapView = ui.graphicsView
        scene = QtWidgets.QGraphicsScene()
        grapView.setScene(scene)
        pendulum = QtGui.QPixmap()
        pendulum.load("./res/pendulum.png")
        scene.addItem(QtWidgets.QGraphicsPixmapItem(pendulum))
        car = QtGui.QPixmap()
        car.load("./res/car.png")
        scene.addItem(QtWidgets.QGraphicsPixmapItem(car))

    def test(self):
        print(self.get_M())
        print(self.get_m())
        print(self.get_L())
        print(self.get_u())
        print(self.get_P())
        print(self.get_I())
        print(self.get_D())


if __name__ == '__main__':

    app = QApplication(sys.argv)
    mainWindow = QMainWindow()
    ui = Ui_Dialog()
    ui.setupUi(mainWindow)
    unite = Unite(ui)
    ui.pushButton.clicked.connect(unite.firstButton)
    ui.pushButton_2.clicked.connect(unite.reset)
    unite.drawInit()

    mainWindow.show()
    sys.exit(app.exec_())
