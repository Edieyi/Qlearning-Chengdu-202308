from RouteParameters import station1
from OperationModel import TrainModel

def Cal_Resistace(cur_S):
    Model = TrainModel()
    station = station1()
    cur_x = cur_S[0]
    cur_v = cur_S[1]

    mass = Model.Mass
    a = Model.a
    b = Model.b
    c = Model.c

    slope = station.calculate_slope(cur_x)
    radius = station.calculate_radius(cur_x)

    f0 = (a + b * cur_v + c * cur_v * cur_v) * mass / 1000
    fg = slope * 9.8 * mass / 1000
    if radius == 0:
        fr = 0
    else:
        fr = 600 / radius * mass * 9.8 / 1000

    fres = - (f0 + fg + fr)
    return fres

# 测试
# state = [20,20]
# f = Cal_Resistace(state)
# print(f)