from env.ms_environment import MinesweeperEnv
import math
import numpy as np
import random
import pickle
import os
import sys

NUM_MINES = 100
WIDTH = 30
HEIGHT = 30

NUM_EPISODES  = 250
LEARNING_RATE = 0.7
GAMMA         = 0.95
MAX_EPSILON   = 1.0
MIN_EPSILON   = 0.01
DECAY_RATE    = 0.005

env = MinesweeperEnv(width=WIDTH,
                     height=HEIGHT,
                     num_mines=NUM_MINES,
                     flood_fill=True,
                     debug=False,
                     punishment=0.01,
                     seed=None,
                     first_move_safe=True,
                     pause_after_end=False)


def board_to_string(board, end='\n'):
    s = ''
    for x in range(board.shape[0]):
        for y in range(board.shape[1]):
            s += str(board[x][y]) + '\t'
        s += end
    return s[:-len(end)]

def main():

    epsilon = 1.0
    action_size = env.action_space.n
    max_steps = env.observation_space.shape[0] * env.observation_space.shape[1]

    file_name = os.path.join(os.path.dirname(__file__), 'q-tables/{}x{}-{}.p'.format(
        env.observation_space.shape[0],
        env.observation_space.shape[1],
        NUM_MINES))

    if os.path.exists(file_name):
        qtable = pickle.load(open(file_name, "rb"))
    else:
        qtable = {}

    rewards = []

    for episode in range(NUM_EPISODES):
        state = env.reset()
        state_str = board_to_string(state)

        if not state_str in qtable:
            qtable[state_str] = np.zeros(action_size)

        done = False
        total_rewards = 0

        for step in range(max_steps):
            exp_exp_tradeoff = random.uniform(0, 1)

            # Exploitation
            if exp_exp_tradeoff > epsilon:
                action = np.argmax(qtable[state_str])
            # Exploration
            else:
                action = env.action_space.sample()
            env.render()
            new_state, reward, done, info = env.step(action)
            env.render()
            new_state_str = board_to_string(new_state)

            if not new_state_str in qtable:
                qtable[new_state_str] = np.zeros(action_size)

            qtable[state_str][action] = qtable[state_str][action] + \
                LEARNING_RATE * (reward + \
                                GAMMA * np.max(qtable[new_state_str]) - \
                                qtable[state_str][action])
            total_rewards += reward

            state = new_state

            if done == True:
                break

        # Reduce epsilon (less exploration as time goes on)
        epsilon = MIN_EPSILON + \
                (MAX_EPSILON - MIN_EPSILON) * np.exp(-DECAY_RATE * episode)
        rewards.append(total_rewards)


    print("Average score: {}".format(sum(rewards)/NUM_EPISODES))
    pickle.dump(qtable, open(file_name, "wb"))


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("Terminated early.")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
