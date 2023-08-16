import numpy as np
from OperationModel import TrainModel

class agent:
    def __init__(self, obs_n, act_n, lr, gamma, epsilon, train_env):
        self.obs_n = obs_n  # 状态空间大小
        self.act_n = act_n  # 动作空间大小
        self.lr = lr
        self.gamma = gamma
        self.epsilon = epsilon
        self.train_env = train_env
        self.Q = np.zeros((obs_n, act_n)) * 0.01
        self.Model = TrainModel()

    def sample(self, obs):
        obs_idx = self.train_env.map_state_to_index(obs)  # 将状态映射为整数索引
        #action = 0
        if np.random.uniform(0, 1) < (1.0 - self.epsilon):
            action = self.predict(obs_idx)  # 使用整数索引来获取动作
        else:
            action = np.random.choice(self.act_n)

        return action

    def predict(self, obs_idx):
        Q_list = self.Q[obs_idx, :]
        maxQ = np.max(Q_list)
        action_list = np.where(Q_list == maxQ)[0]
        action = np.random.choice(action_list)

        return action

    def learn(self, obs, action, reward, next_obs, done):
        obs_idx = obs  # 使用状态索引
        next_obs_idx = next_obs  # 使用下一个状态索引
        next_obs_idx = np.clip(next_obs_idx, 0, self.obs_n - 1)
        predict_Q = self.Q[obs_idx, action]
        #print(predict_Q)
        if done == False:
            target_Q = reward
        else:
            target_Q = reward + self.gamma * np.max(self.Q[next_obs_idx])
        self.Q[obs_idx, action] += self.lr * (target_Q - predict_Q)