
class station1:
    def __init__(self):
        self.start_station = "Jin Xing"  # 起始站
        self.end_station = "Huang Shi"  # 终点站
        self.station_distance = 4280  # 线路站间长度
        self.delt_pos = 40  # 位置离散
        self.scheduled_time = 173  # 计划运行时间
        self.limit_speed = {0: 100, 547: 140, 2958: 115, 3298: 100, 4280: 0}  # 区间限速
        self.slope = {0: 0, 335: -8.97, 1285: 0, 2185: -5.9, 4025: 0}  # 区间坡度
        self.radius = {0: 0, 131: 1000, 253: 0, 1575: 5004, 1715: 0, 3134: 1004,
                               3462: 0, 3674: 600, 3993:0}  # 区间曲率
        self.true_traction_E = 87.98  # 牵引能耗
        self.true_re_E = 58.42  # 再生能
        self.true_E = 29.56  # 实际运行能耗

    def calculate_speed(self, x):  # 计算某位置处的限速
        sorted_positions = sorted(self.limit_speed.keys())

        for i in range(len(sorted_positions) - 1):
            start_position = sorted_positions[i]
            end_position = sorted_positions[i + 1]

            if start_position <= x < end_position:
                return self.limit_speed[start_position]

        return self.limit_speed[sorted_positions[-1]]

    def calculate_slope(self, x): # 计算某位置处的坡度
        sorted_positions = sorted(self.slope.keys())

        for i in range(len(sorted_positions) - 1):
            start_position = sorted_positions[i]
            end_position = sorted_positions[i + 1]

            if start_position <= x < end_position:
                return self.slope[start_position]

        return self.slope[sorted_positions[-1]]

    def calculate_radius(self, x): # 计算某位置处的曲率
        sorted_positions = sorted(self.radius.keys())

        for i in range(len(sorted_positions) - 1):
            start_position = sorted_positions[i]
            end_position = sorted_positions[i + 1]

            if start_position <= x < end_position:
                return self.radius[start_position]

        return self.radius[sorted_positions[-1]]







# 测试
# station_name = station1()
# 使用calculate_speed函数计算特定距离处的速度
# distance_to_calculate = 3135
# calculated_speed = station_name.calculate_speed(distance_to_calculate)
# calculated_slope = station_name.calculate_slope(distance_to_calculate)
# calculated_radius = station_name.calculate_radius(distance_to_calculate)
# print(f"在距离 {distance_to_calculate} 处的计算速度为: {calculated_speed}")
# print(f"在距离 {distance_to_calculate} 处的计算坡度为: {calculated_slope}")
# print(f"在距离 {distance_to_calculate} 处的计算曲率为: {calculated_radius}")