import numpy as np
from RouteParameters import station1
import matplotlib.pyplot as plt

class TrainModel():
    def __init__(self):
        #super(TrainEnvironment, self).__init__()
        #列车参数
        self.Mass = 337800  #千克

        #戴维斯系数
        self.a = 8.4
        self.b = 0.1071
        self.c = 0.0042

        #效率系数
        self.n1 = 1  # 牵引电机效率
        self.n1_b = 1  # 制动电机效率
        self.n2 = 0.9702  # 变压器效率
        self.n3 = 0.96  # 变流器效率
        self.n4 = 0.97  # 齿轮箱效率


        self.max_traction = 0
        self.max_brake = 0
        self.traction_E = 0
        self.re_E = 0

    #最大牵引力
    def get_max_traction(self, cur_v): # 速度为km/h
        current_v = cur_v * 3.6
        if current_v <= 57:
            self.max_traction = 409
        if 57 < current_v <= 140:
            self.max_traction = 0.02893 * current_v * current_v - 8.417 * current_v + 785.8
        return self.max_traction

    #最大制动力
    def get_max_brake(self, cur_v):
        current_v = cur_v * 3.6 # 速度为km/h
        if current_v <= 6:
            self.max_brake = 63.29 * current_v
        if 6 < current_v <= 100:
            self.max_brake = 379.75
        if 100 < current_v <=140:
            self.max_brake = -2.685 * current_v + 642

        return self.max_brake

    # 计算牵引电机效率
    def get_n1(self, cur_v):  # 速度单位为km/h
        current_v = cur_v * 3.6
        if current_v <= 55:
            self.n1 = -0.802 * np.exp(-0.1467 * current_v) + 0.8904
        else:
            self.n1 = 0.927

        return self.n1

    # 计算制动电机效率
    def get_n1_b(self, cur_v):
        current_v = cur_v * 3.6 # 速度单位为km/h
        if 0 < current_v <= 60:
            self.n1_b = -0.09175 * np.exp(17 / current_v) + 1.048
            if self.n1_b < 0:
                self.n1_b = 0
        else:
            self.n1_b = 0.94
        return self.n1_b

    #牵引能耗
    def get_traction_E(self, cur_v, average_v, delt_t):
        if self.n1 == 0 or self.n2 == 0 or self.n3 == 0 or self.n4 == 0:
            # 处理参数为零的情况，例如设置默认值或进行修正
            return 0
        else:
            self.n1 = self.get_n1(cur_v)
            self.max_traction =self.get_max_traction(cur_v)
            self.traction_E = self.max_traction * average_v * delt_t / \
                              (self.n1 * self.n2 * self.n3 * self.n4 * 3600)

        return self.traction_E

     #再生能
    def get_re_E(self,cur_v,average_v, delt_t):
        if self.n1 == 0 or self.n2 == 0 or self.n3 == 0 or self.n4 == 0:
            # 处理参数为零的情况，例如设置默认值或进行修正
            return 0
        else:
            self.n1_b = self.get_n1_b(cur_v)
            self.max_brake = self.get_max_brake(cur_v)
            ave_v = average_v
            self.re_E = abs(self.max_brake * ave_v * delt_t * (self.n1_b *
                        self.n2 * self.n3 * self.n4) / 3600)
        return self.re_E

    #阻力计算
    def Cal_Resistace(self, cur_S):
        station = station1()
        cur_x = cur_S[0]
        cur_v = cur_S[1] * 3.6


        slope = station.calculate_slope(cur_x)
        radius = station.calculate_radius(cur_x)

        f0 = (self.a + self.b * cur_v + self.c * cur_v * cur_v) * self.Mass / 1000
        fg = slope * 9.8 * self.Mass / 1000
        if radius == 0:
            fr = 0
        else:
            fr = 600 / radius * self.Mass * 9.8 / 1000

        fres = - (f0 + fg + fr)
        return fres

    #站1的最速曲线
    def limit_v_curve(self):
        vt = 0
        v1 = [0]

        amax = 1.5
        amin = -1.3

        s0 = (100 / 3.6) ** 2 / (2 * amax)
        s1 = ((140 / 3.6) ** 2 - (100 / 3.6) ** 2) / (2 * amax) + 547
        s2 = 2958 - ((140 / 3.6) ** 2 - (115 / 3.6) ** 2) / (2 * abs(amin))
        s3 = 3298 - ((115 / 3.6) ** 2 - (100 / 3.6) ** 2) / (2 * abs(amin))
        s4 = 4280 - ((100 / 3.6) ** 2) / (2 * abs(amin))

        for s in range(1, 4281):
            if s < s0:
                v1.append(np.sqrt(2 * amax * s))
            elif s >= s0 and s < 547:
                v1.append(100 / 3.6)
            elif s >= 547 and s < s1:
                v1.append(np.sqrt((100 / 3.6) ** 2 + 2 * amax * (s - 547)))
            elif s >= s1 and s < s2:
                v1.append(140 / 3.6)
            elif s >= s2 and s < 2958:
                v1.append(np.sqrt((140 / 3.6) ** 2 + 2 * amin * (s - s2)))
            elif s >= 2958 and s < s3:
                v1.append(115 / 3.6)
            elif s >= s3 and s < 3298:
                v1.append(np.sqrt((115 / 3.6) ** 2 + 2 * amin * (s - s3)))
            elif s >= 3298 and s < s4:
                v1.append(100 / 3.6)
            elif s >= s4 and s < 4280:
                v1.append(np.sqrt((100 / 3.6) ** 2 + 2 * amin * (s - s4)))
            else:
                v1.append(0)

        return v1

#测速最速曲线
# station_1_limitV = TrainModel()
# curve = station_1_limitV.limit_v_curve()
# print(curve)
# plt.plot(curve)
# plt.show()

