from math import sqrt
import numpy as np
from OperationModel import TrainModel
from RouteParameters import station1
import time

class Train_environment:
    # 初始化参数
    def __init__(self, episode, agent, num_position_bins, num_velocity_bins):
        self.cur_v = 0  # 当前速度，初始化速度为0
        self.cur_x = 0  # 当前位置，初始化为起点
        self.cur_S = [self.cur_x, self.cur_v] # 当前状态

        self.next_v = 0  # 下一状态速度
        self.next_x = 0  # 下一站状态位置
        self.next_S = []  # 下一状态
        self.acc = 0  # 合力加（减）速度
        self.action = 0
        self.delt_t = 0

        self.delt_x = 40  # 位置间隔，时间步
        self.delt_v = 1
        self.Model = TrainModel()
        self.station_distance = 4280

        self.energy_weight = 0.2
        self.time_weight = 0.8

        self.episode = episode
        self.agent = agent

        self.num_position_bins = num_position_bins
        self.num_velocity_bins = num_velocity_bins

        self.episode_start_time = None
        self.actual_runtimes = []

        self.positions_history = []
        self.velocities_history = []

    # 计算位置和速度的离散索引
    def  map_state_to_index(self, state):
        if np.any(np.isnan(state)):
            # 处理状态中包含 NaN 的情况
            raise ValueError("State contains NaN values")

        # 计算位置的离散索引，并确保不超过 num_position_bins
        position_idx = int(state[0] / self.delt_x) % self.num_position_bins

        # 计算速度的离散索引，并确保不超过 num_velocity_bins
        velocity_idx = int(state[1]) % self.num_velocity_bins

        state_to_index = position_idx * self.num_velocity_bins + velocity_idx

        return state_to_index


    # 根据动作空间计算加速度
    def calculate_acc(self, cur_S):
        cur_x = cur_S[0]
        cur_v = cur_S[1] # 速度为m/s

        if cur_v == 0:
            max_F = self.Model.get_max_traction(cur_v)
            fres = self.Model.Cal_Resistace(cur_S)
            self.acc = (max_F * 1000 - fres) / self.Model.Mass

        elif cur_x >= self.station_distance * 0.9 and cur_v > 0:
            # 这里根据你的物理模型合理选择减速度大小
            options = [4]
            action = np.random.choice(options)
            if action == 3:  # 50%的最大制动
                max_B = self.Model.get_max_brake(cur_v) * 0.5
                fres = self.Model.Cal_Resistace(cur_S)
                self.acc = (-(max_B * 1000 + fres)) / self.Model.Mass

            if action == 4:
                max_B = self.Model.get_max_brake(cur_v)
                fres = self.Model.Cal_Resistace(cur_S)
                self.acc = (-(max_B * 1000 + fres)) / self.Model.Mass
        else:
            action = self.agent.sample(cur_S)
            if action == 0:  # 最大牵引
                max_F = self.Model.get_max_traction(cur_v)
                fres = self.Model.Cal_Resistace(cur_S)
                self.acc = (max_F * 1000 - fres) / self.Model.Mass

            if action == 1:  # 50%的最大牵引
                max_F = self.Model.get_max_traction(cur_v) * 0.5
                fres = self.Model.Cal_Resistace(cur_S)
                self.acc = (max_F * 1000 - fres) / self.Model.Mass

            if action == 2:  # 惰行
                fres = self.Model.Cal_Resistace(cur_S)
                self.acc = - fres / self.Model.Mass

            if action == 3:  # 50%的最大制动
                max_B = self.Model.get_max_brake(cur_v) * 0.5
                fres = self.Model.Cal_Resistace(cur_S)
                self.acc = (-(max_B * 1000 + fres)) / self.Model.Mass

            if action == 4:
                max_B = self.Model.get_max_brake(cur_v)
                fres = self.Model.Cal_Resistace(cur_S)
                self.acc = (-(max_B * 1000 + fres)) / self.Model.Mass



        low_bound = -1.3
        upper_bound = 1.5
        self.acc = np.clip(self.acc, low_bound, upper_bound)


        #self.action = action  # 将计算后的动作保存起来

    # 计算下一状态空间
    def calculate_next_state(self, cur_S):
        cur_x = cur_S[0]
        cur_v = cur_S[1] # 速度为m/s

        temp_v = cur_v * cur_v + 2 * self.acc * self.delt_x
        if temp_v <= 0:
            temp_v = 0

        # 获取限制速度曲线函数计算出的速度
        limit_v = self.Model.limit_v_curve()[int(cur_x)]
        #print(limit_v)
        # 将速度限制在较小的值（限制速度曲线计算出的速度和计算出的速度）中
        if cur_x == 0:
            self.next_v = np.sqrt(temp_v)
        else:
            self.next_v = min(np.sqrt(temp_v), limit_v)

        self.next_x = cur_x + self.delt_x
        self.next_S = [self.next_x, self.next_v]

        if np.isnan(self.next_v):  # 检查下一个速度是否为NaN
            raise ValueError("Next velocity is NaN")

        return self.next_S

    # 计算两状态间列车运行时间
    def calculate_run_time(self):
        self.delt_t = abs((self.next_S[1] - self.cur_S[1]) / self.acc)
        return self.delt_t

    # 计算两状态间能耗
    def calculate_energy(self):
        ave_v = 0.5 * (self.cur_S[1] + self.next_S[1])
        # 计算运行时间（两状态间的）
        delt_t = self.calculate_run_time()

        # 计算能耗
        if self.acc > 0:
            energy_E1 = self.Model.get_traction_E(self.cur_S[1], ave_v, delt_t)  # 牵引能耗
            energy_E2 = 0
        if self.acc < 0:
            energy_E1 = 0
            energy_E2 = self.Model.get_re_E(self.cur_S[1], ave_v, delt_t)  # 再生制动

        energy = energy_E1 - energy_E2# 总能耗

        return energy

    # 计算奖励函数
    def calculate_reward(self):
        ave_v = 0.5 * (self.cur_S[1] + self.next_S[1])

        energy = self.calculate_energy()
        run_time = self.calculate_run_time()
        chengfa = 0

        #if ave_v <=0:
            #chengfa = -100

        # 根据实际运行时间和权重计算准时性奖励
        #reward = (self.energy_weight * energy + self.time_weight *abs(run_time - ave_v) )
        reward = -energy
        #reward = -(self.energy_weight * energy + self.time_weight * (173 - actual_runtime)

        return reward, energy

    # 复位
    def reset(self):
        self.cur_v = 0
        self.cur_x = 0
        self.cur_S = [self.cur_x, self.cur_v]

        self.positions_history = []  # 重置位置历史数据列表
        self.velocities_history = []  # 重置速度历史数据列表

    #一个step的状态转移
    def step(self, action):
        self.calculate_acc(self.cur_S)
        self.next_S = self.calculate_next_state(self.cur_S)
        print(self.next_S[1])
        reward, energy = self.calculate_reward()

        # 记录位置和速度的历史数据
        self.positions_history.append(self.cur_S[0])
        self.velocities_history.append(self.cur_S[1])


        if self.next_S[0] > 4280:
            self.next_S[0] = 4280
            self.next_S[1] = 0
            if self.next_S == [4280, 0]:
                done = True
            else:
                done = False
        else:
            done = False

        if np.any(np.isnan(self.next_S)):  # 检查下一个状态是否包含NaN值
            raise ValueError("Next state contains NaN values")

        return self.next_S, reward, energy,  done

    # 获取位置信息
    def get_positions_history(self):
        return self.positions_history

    # 获取速度信息
    def get_velocities_history(self):
        return self.velocities_history





