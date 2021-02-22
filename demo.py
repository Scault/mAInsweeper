import gym
from ms_environment import MinesweeperEnv
import time

# TODO: adjust the recursion limit according to the window size
# import sys
# sys.setrecursionlimit(10000)

# Change if you would like to step through each iteration
WAIT_BEFORE_EVERY_STEP = False

NUM_EPISODES = 200

if WAIT_BEFORE_EVERY_STEP:
    print("Press any key to advance the instance...")

env = MinesweeperEnv(width=30,
                     height=30,
                     num_mines=100,
                     flood_fill=True,
                     debug=False,
                     punishment=0.01,
                     seed=None,
                     first_move_safe=True,
                     pause_after_end=False)

for i_episode in range(NUM_EPISODES):
    observation = env.reset()
    for t in range(100):
        env.render()

        if WAIT_BEFORE_EVERY_STEP:
            env.window.wait()

        action = env.action_space.sample()
        observation, reward, done, info = env.step(action)
        if done:
            print("Episode finished after {} moves.".format(t+1))
            break

env.close()
