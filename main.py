import cgitb
import sys

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from lib import Single_inverted_pendulum
from res import Ui_Dialog

cgitb.enable(format='text')


class Animation(QObject):
    def __init__(self, item):
        super().__init__()
        
        self.item = item
        self.dur = 1000
        self.anim_move = QPropertyAnimation()
        self.anim_rotate = QPropertyAnimation()

    def move(self, x,y):  # p:QPointF(250, 20)
        self.anim_move = QPropertyAnimation(self, b'pos')
        self.anim_move.setDuration(self.dur)
        self.anim_move.setStartValue(QPointF(self.item.x(), self.item.y()))
        self.anim_move.setEndValue(QPointF(x, y))

    def rotate(self, a):  # a:360
        self.anim_rotate = QPropertyAnimation(self, b'rotation')
        self.anim_rotate.setDuration(self.dur)
        self.anim_rotate.setStartValue(QPointF(self.item.rotation(), 1))
        self.anim_rotate.setEndValue(QPointF(a, 1))

    def start(self, isM=False, isR=False):
        if isM:
            self.anim_move.start()
        if isR:
            self.anim_rotate.start()

    def __set_pos(self, pos):
        self.item.setPos(pos)  # 位置

    def __set_rotation(self, angle):
        self.item.setRotation(angle.x())  # 旋转度数

    pos = pyqtProperty(QPointF, fset=__set_pos)
    rotation = pyqtProperty(QPointF, fset=__set_rotation)


class Unite():
    def __init__(self, ui):
        self.ang=0
        self.dis=0
        self.ui = ui
        self.ctrl = Single_inverted_pendulum(self.fun_timer)

        self.cross_bar_item = QGraphicsPixmapItem()
        self.pendulum_item = QGraphicsPixmapItem()
        self.car_item = QGraphicsPixmapItem()
        self.drawInit()
        self.pendulum_anim = Animation(self.pendulum_item)
        self.car_anim = Animation(self.car_item)

        self.pendulum_x_offset
        self.pendulum_y_offset
        self.car_x_offset
        self.car_y_offset

        self.reseted = True
        self.pressed = False
        self.ctrl.start()
        self.ctrl.pause()

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
        self.ctrl.reset()
        self.ctrl.pause()
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
        self.ctrl.resume()

        # print("start")
        ui.pushButton.setText("   暂停")

    def __pause(self):
        self.pressed = False

        # print("pause")
        self.ctrl.pause()
        ui.pushButton.setText("   继续")

    def __continue(self):
        self.pressed = True

        # print("continue")
        self.ctrl.set(
            mCart=self.get_M(),
            mPend=self.get_m(),
            L=self.get_L(),
            b=self.get_u(),
            Kp=self.get_P(),
            Ki=self.get_I(),
            Kd=self.get_D())
        self.ctrl.resume()
        ui.pushButton.setText("   暂停")

    # 动画部分
    def drawInit(self):
        grapView = ui.graphicsView
        scene = QtWidgets.QGraphicsScene()
        width = 551
        height = 551
        grapView.setScene(scene)
        scene.setSceneRect(0, 0, width, height)

        cross_bar_w = 551
        cross_bar_h = 10
        cross_bar = QPixmap("./res/cross_bar.png").scaled(
            cross_bar_w, cross_bar_h)
        self.cross_bar_item = QGraphicsPixmapItem(cross_bar)  # cross_bar
        scene.addItem(self.cross_bar_item)
        self.cross_bar_item.setPos(QPointF(0, height * 2 / 3))
        self.cross_bar_item.setZValue(0)

        car_w = 70
        car_h = 46
        self.car_x_offset=0-car_w/2
        self.car_y_offset=0-car_h
        car = QPixmap("./res/car.png").scaled(car_w, car_h)
        self.car_item = QGraphicsPixmapItem(car)  # car
        scene.addItem(self.car_item)
        self.car_item.setPos(
            QPointF(width / 2 - car_w / 2,
                    height * 2 / 3 - car_h / 2 + cross_bar_h / 2))
        self.car_item.setZValue(2)

        pendulum_w = 10
        pendulum_h = 201
        self.pendulum_x_offset=0-pendulum_w/2
        self.pendulum_y_offset=0-pendulum_h
        self.pendulum = QPixmap("./res/pendulum.png").scaled(
            pendulum_w, pendulum_h)
        self.pendulum_item = QGraphicsPixmapItem(self.pendulum)  # pendulum
        scene.addItem(self.pendulum_item)
        self.pendulum_item.setPos(
            QPointF(width / 2 - pendulum_w / 2,
                    self.car_item.y() - pendulum_h))
        self.pendulum_item.setTransformOriginPoint(pendulum_w / 2,
                                                   pendulum_h)  # 设置旋转中心
        self.pendulum_item.setZValue(1)

    def fun_timer(self):
        self.ang+=1
        self.dis+=0.1
        # result=self.ctrl.get_ang_dis()
        # print(result[1],result[0])
        # self.animation(result[1],result[0])
        self.animation(self.dis,self.ang)


    def animation(self,x,a):
        print("animation")
        
        self.pendulum_anim.dur=1
        self.pendulum_anim.move(x+self.pendulum_x_offset, self.pendulum_item.y())
        # self.pendulum_anim.rotate(a)
        self.pendulum_anim.start(isM=True)

        self.car_anim.dur = 2
        self.car_anim.move(x+self.car_x_offset, self.car_item.y())
        self.car_anim.start(isM=True)

    def __test(self):
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = QMainWindow()
    ui = Ui_Dialog()
    ui.setupUi(mainWindow)
    unite = Unite(ui)
    ui.pushButton.clicked.connect(unite.firstButton)
    ui.pushButton_2.clicked.connect(unite.reset)



    mainWindow.show()
    # def fun_timer():
    #     result = car.get_ang_dis()
       
    

    sys.exit(app.exec_())
