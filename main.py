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
        self.anim_move = QPropertyAnimation()
        self.anim_rotate = QPropertyAnimation()

    def move(self, p0, p1, dur=5000):  # p0:QPointF(250, 20)
        self.anim_move = QPropertyAnimation(self, b'pos')
        self.anim_move.setDuration(dur)
        self.anim_move.setStartValue(p0)
        self.anim_move.setEndValue(p1)

    def rotate(self, a0, a1, dur=5000):  # a:360
        self.anim_rotate = QPropertyAnimation(self, b'rotation')
        self.anim_rotate.setDuration(dur)
        self.anim_rotate.setStartValue(QPointF(a0, 1))
        self.anim_rotate.setEndValue(QPointF(a1, 1))

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
        self.ui = ui
        self.ctrl = Single_inverted_pendulum(self.fun_timer)

        self.cross_bar_item = QGraphicsPixmapItem()
        self.pendulum_item = QGraphicsPixmapItem()
        self.car_item = QGraphicsPixmapItem()
        self.drawInit()
        self.pendulum_anim = Animation(self.pendulum_item)
        self.car_anim = Animation(self.car_item)

        self.reseted = True
        self.pressed = False

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
        # self.anim.start()
        self.animation()

        # print("start")
        ui.pushButton.setText("   暂停")

    def __pause(self):
        self.pressed = False

        # print("pause")
        ui.pushButton.setText("   继续")

    def __continue(self):
        self.pressed = True

        # print("continue")
        ui.pushButton.setText("   暂停")

    def fun_timer():
        # print('hello timer')   #打印输出
        global result1
        global result2
        result1 = []
        result2 = []
        result = car.get_ang_dis()
        result1.append(result[0])
        result2.append(result[1])
        print(car.t_index)
        if (len(result2) > 400):
            # plot
            print('8s采样实际耗时：', (clock() - start))
            t = np.linspace(
                0, len(result2) * 0.02, len(result2), endpoint=False)
            plt.figure()
            plt.subplot(2, 1, 1)
            plt.plot(t, result1)
            plt.subplot(2, 1, 2)
            plt.plot(t, result2)
            plt.show()
            car.stop()

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
        car = QPixmap("./res/car.png").scaled(car_w, car_h)
        self.car_item = QGraphicsPixmapItem(car)  # car
        scene.addItem(self.car_item)
        self.car_item.setPos(
            QPointF(width / 2 - car_w / 2,
                    height * 2 / 3 - car_h / 2 + cross_bar_h / 2))
        self.car_item.setZValue(2)

        pendulum_w = 10
        pendulum_h = 201
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

    def animation(self):
        self.pendulum_anim.move(
            QPointF(self.pendulum_item.x(), self.pendulum_item.y()),
            QPointF(self.pendulum_item.x(), self.pendulum_item.y()))
        self.pendulum_anim.rotate(0, 200)
        self.pendulum_anim.start(isM=True, isR=True)

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
    sys.exit(app.exec_())
