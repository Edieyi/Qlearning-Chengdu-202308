from OperationModel import TrainModel
import numpy as np
class Env:
    def __init__(self):
        self.cur_v = 0
        self.cur_x = 0
        self.cur_S = [self.cur_x, self.cur_v]
        self.next_v = 0
        self.next_x = 0
        self.next_S = []
        self.acc = 0
        self.action = 0
        self.delt_t = 0
        self.delt_x = 40
        self.delt_v = 1
        self.Model = TrainModel()

    def calculate_acc(self, action, cur_S):
        cur_x = cur_S[0]
        cur_v = cur_S[1]

        if action == 1:
            max_F = self.Model.get_max_traction(cur_v)
            fres = self.Model.Cal_Resistace(cur_S)
            self.acc = (max_F*1000 - fres) / self.Model.Mass
            print(max_F)
            print(fres)

        if action == 2:
            max_F = self.Model.get_max_traction(cur_v) * 0.5
            fres = self.Model.Cal_Resistace(cur_S)
            self.acc = (max_F*1000 - fres) / self.Model.Mass

        if action == 3:
            fres = self.Model.Cal_Resistace(cur_S)
            self.acc = - fres / self.Model.Mass

        if action == 4:
            max_B = self.Model.get_max_brake(cur_v) * 0.5
            fres = self.Model.Cal_Resistace(cur_S)
            self.acc = (-(max_B*1000 + fres)) / self.Model.Mass

        if action == 5:
            max_B = self.Model.get_max_brake(cur_v)
            fres = self.Model.Cal_Resistace(cur_S)
            self.acc = (-(max_B*1000 + fres)) / self.Model.Mass

        low_bound = -1.3
        upper_bound = 1.5
        self.acc = np.clip(self.acc, low_bound, upper_bound)
        self.action = action
        return self.acc

env_instance = Env()
state = [40, 9.61]
a = env_instance.calculate_acc(1, state)
print(a)
