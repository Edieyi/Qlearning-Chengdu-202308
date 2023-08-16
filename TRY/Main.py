from Env import Train_environment
from QlearningAgent import agent
from RouteParameters import station1
import numpy as np
import matplotlib.pyplot as plt

def main():
    # 初始化环境
    station = station1
    episode = 100 # 你的回合数
    max_velocity = 40
    num_position_bins = int(4280 / 40)
    num_velocity_bins = int(max_velocity / 1) + 1
    obs_n = num_velocity_bins * num_position_bins  # 状态空间大小
    act_n = 5  # 动作空间大小
    lr = 0.01  # 学习率
    gamma = 0.99  # 折扣因子
    epsilon = 0.2  # 探索概率

    np.random.seed(4)

    train_env = Train_environment(episode, None, num_position_bins, num_velocity_bins)  # 将 age nt 参数设为 None
    train_agent = agent(obs_n, act_n, lr, gamma, epsilon, train_env)   # 不需要传递 train_env 实例
    train_env.agent = train_agent

    total_rewards_per_episode = []  # 创建一个空列表用于存储每个 episode 的总奖励

    highest_total_reward = float("-inf")  # 用于记录最高总奖励
    best_episode_data = None  # 用于记录最高总奖励的 episode 数据

    for episode in range(1, episode + 1):
        train_env.reset()  # 重置环境
        total_reward = 0  # 用于累积每个 episode 的总奖励
        done = False
        total_energy = 0



        while not done:
            state_idx = train_env.map_state_to_index(train_env.cur_S)  # 获取状态索引

            action = train_agent.sample(train_env.cur_S)  # 代理根据状态选择动作
            next_state, reward, energy, done = train_env.step(action)  # 环境执行动作，更新状态
            total_reward += reward  # 累积奖励值
            total_energy += energy
            # 记录位置和速度的历史数据
            train_env.positions_history.append(train_env.cur_x)
            train_env.velocities_history.append(train_env.cur_v)

            if done:
                break

            done = (train_env.cur_x > 4280)  # 判断是否达到终止条件

            # 打印每个 step 的状态和奖励值
            print(
                f"Episode: {episode}, Step reward: {reward}, Current state: {train_env.cur_S}, Next state: {next_state}")

            #done = (train_env.cur_x >= 4279.5)  # 判断是否达到终止条件
            train_agent.learn(state_idx, action, reward, train_env.map_state_to_index(next_state), done)  # 代理学习
            train_env.cur_S = next_state  # 更新当前状态

        total_rewards_per_episode.append(total_reward)  # 在每个 episode 循环结束后将总奖励值添加到列表中

        # 打印每个 episode 的总分数
        print(f"Episode {episode} finished. Total reward: {total_reward}")

        # 更新最高总奖励和对应的 episode 数据
        if total_reward > highest_total_reward:
            highest_total_reward = total_reward
            best_episode_data = {
                "episode": episode,
                "total_reward": total_reward,
                "total_energy": total_energy,
                "positions": train_env.get_positions_history(),
                "velocities": train_env.get_velocities_history()
            }

        # 计算最低总奖励的 episode 数据
        lowest_total_reward = min(total_rewards_per_episode)
        lowest_episode_index = total_rewards_per_episode.index(lowest_total_reward)
        best_episode_data_lowest = {
            "episode": lowest_episode_index + 1,
            "total_reward": lowest_total_reward,
            "total_energy": total_energy,
            "positions": train_env.get_positions_history(),
            "velocities": train_env.get_velocities_history()
        }

    # 绘制图形
    plt.plot(range(1, episode + 1), total_rewards_per_episode, marker='o')
    plt.xlabel('Episode')
    plt.ylabel('Total Reward')
    plt.title('Total Reward per Episode')
    plt.grid()
    plt.show()

    # 绘制最高总奖励 episode 的位置-速度图
    if best_episode_data is not None:
        positions = best_episode_data["positions"]
        velocities = best_episode_data["velocities"]
        energy = best_episode_data["total_energy"]
        print(energy)

        sorted_indices = np.argsort(positions)  # 对位置数据进行排序
        sorted_positions = np.array(positions)[sorted_indices]
        sorted_velocities = np.array(velocities)[sorted_indices]

        plt.plot(sorted_positions, sorted_velocities)
        plt.xlabel('Position')
        plt.ylabel('Velocity')
        plt.title(f'Position-Velocity Plot for Best Episode (Episode {best_episode_data["episode"]})')
        plt.grid()
        plt.show()


    # 绘制最低总奖励 episode 的位置-速度图
    if best_episode_data is not None:
        positions_lowest = best_episode_data_lowest["positions"]
        velocities_lowest = best_episode_data_lowest["velocities"]
        energy = best_episode_data_lowest["total_energy"]
        print("----------------min reward-----------")
        print(energy)

        sorted_indices_lowest = np.argsort(positions_lowest)  # 对位置数据进行排序
        sorted_positions_lowest = np.array(positions_lowest)[sorted_indices_lowest]
        sorted_velocities_lowest = np.array(velocities_lowest)[sorted_indices_lowest]

        plt.plot(sorted_positions_lowest, sorted_velocities_lowest)
        plt.xlabel('Position')
        plt.ylabel('Velocity')
        plt.title(f'Position-Velocity Plot for Lowest Episode (Episode {best_episode_data_lowest["episode"]})')
        plt.grid()
        plt.show()

if __name__ == '__main__':
    main()
