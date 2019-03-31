import math
import threading
from time import clock

import numpy as np
from control.matlab import *
from matplotlib import pyplot as plt
from scipy import signal


class Single_inverted_pendulum():
    def __init__(self):
        self.last_state = [0, 0]  #迭代计算的关键
        self.stop_flag = False  #暂停的标志
        self.t_index = 0  #自身维护的输出点的计数
        self.dt = 0.02  #采样间隔
        self.input_pulse = self.get_pulse_sampling(
            0, 1, self.dt, during=0.02)  #设置系统的pulse输入，就是类似于一个瞬间冲击
        self.set()  # 设置系统参数

    def get_pulse_sampling(self, start, stop, step, during=0.02):
        '''
        获取pulse采样
        :param stop:
        :param step:
        :param during: pulse持续时间
        :return:
        '''
        # 计算总数，不包含stop
        if stop < start or step < 0:
            return
        num = int(math.ceil((stop - start) / step))
        t = np.linspace(start, stop, num, endpoint=False)
        pulse_num = int(math.floor(during / step))
        pulse_value = 1 / during
        u = [pulse_value] * pulse_num + [0] * (len(t) - pulse_num)
        return u, t

    def set(self, mCart=0.5, mPend=0.2, L=0.6, b=0.1, Kp=100, Ki=1, Kd=30):
        r'''
        :param mCart: 小车质量
        :param mPend: 摆的质量
        :param L: 杆长
        :param b: 阻尼系数 N/m/sec
        :param Kp:  比例部分 H=Kp
        :param Ki:  积分部分 H=Ki/s
        :param Kd:  微分部分 H=Kd*s
        :return: T1: 角度传递函数 竖直为0，向左偏为正 单位：rad
                 T2: 位置传递函数 向右为正    单位：m
        '''
        L = L / 2
        g = 9.8
        I = mPend * (2 * L)**2 / 3  #m*l**2/3
        q = (mCart + mPend) * (I + mPend * L**2) - (mPend * L)**2
        P_cart = tf([(I + mPend * L**2) / q, 0, -mPend * g * L / q], [
            1, (b * (I + mPend * L**2)) / q,
            -(mCart + mPend) * mPend * g * L / q, -b * mPend * g * L / q, 0
        ])
        P_pend = tf([mPend * L / q, 0], [
            1, (b * (I + mPend * L**2)) / q,
            -(mCart + mPend) * mPend * g * L / q, -b * mPend * g * L / q
        ])
        C = tf([Kd, Kp, Ki], [1, 0])
        # 角度传递函数
        self.sys_ang = feedback(P_pend, C)
        # 距离传递函数
        self.sys_dis = feedback(1, P_pend * C) * P_cart

    def get_ang_dis(self):
        '''
        获取下一时刻的ang和dis
        :return:
        '''
        if (self.t_index + 1) < len(self.input_pulse[0]) - 1:
            u = [
                self.input_pulse[0][self.t_index],
                self.input_pulse[0][self.t_index + 1]
            ]
        else:
            u = [0, 0]
        t = [self.t_index * self.dt, (self.t_index + 1) * self.dt]
        angle = lsim(self.sys_ang, U=u, T=t, X0=self.last_state[0])
        self.last_state[0] = angle[2][1]

        dis = lsim(self.sys_dis, U=u, T=t, X0=self.last_state[1])
        self.last_state[1] = dis[2][1]
        self.t_index += 1
        return angle[0][0], dis[0][0]

    def stop(self):
        self.stop_flag = True

    def resume(self):
        '''
        先传递参数,然后启动timer
        :return:
        '''
        self.set()  #前端需要传递参数，并做非0等判断
        self.stop_flag = False
        global timer  # 定义变量
        timer = threading.Timer(2, fun_timer)  # 数字是时间
        timer.start()

    def reset(self):
        '''
        时间从0开始计算
        :return:
        '''
        self.t_index = 0
        self.last_state = [0, 0]
        self.stop_flag = True


if __name__ == "__main__":

    def fun_timer():
        # print('hello timer')   #打印输出
        global result1
        global result2

        print(car.t_index)
        if (len(result2) > 400):
            #plot
            t = np.linspace(
                0, len(result2) * 0.02, len(result2), endpoint=False)
            plt.figure()
            plt.subplot(2, 1, 1)
            plt.plot(t, result1)
            plt.subplot(2, 1, 2)
            plt.plot(t, result2)
            plt.show()
        else:
            global timer  # 定义变量
            timer = threading.Timer(0.02, fun_timer)  # 60秒调用一次函数
            # 定时器构造函数主要有2个参数，第一个参数为时间，第二个参数为函数
            if not car.stop_flag:
                timer.start()  # 启用定时器
            result = car.get_ang_dis()
            result1.append(result[0])
            result2.append(result[1])

    result1 = []
    result2 = []
    car = Single_inverted_pendulum()
    if not car.stop_flag:
        timer = threading.Timer(1, fun_timer)  # 首次启动
        timer.start()
