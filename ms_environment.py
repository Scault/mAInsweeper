import gym
import numpy as np
import random

class MinesweeperEnv(gym.Env):
    metadata = {'render.modes': ["ansi", "window"]}
    reward_range = (-float(1), float(1))

    def __init__(self, width=8, height=8, num_mines=10, flood_fill=True,
                 debug=True, punishment=0.01, seed=None, first_move_safe=True,
                 pause_after_end=False):
        self.width = width
        self.height = height
        self.num_mines = num_mines

        self.flood_fill = flood_fill
        self.debug = debug
        self. punishment = punishment
        self.first_move_safe = first_move_safe
        self.pause_after_end = pause_after_end

        self.window = None
        self.observation_space = gym.spaces.Box(low=np.float32(-2),
                                                high=np.float32(8),
                                                shape=(self.width, self.height))
        self.action_space = gym.spaces.Discrete(self.width * self.height)
        self.NEIGHBORS = [(-1, -1), (0, -1), ( 1, -1),
                          (-1,  0), (0,  0), ( 1,  0),
                          (-1,  1), (0,  1), ( 1,  1)]
        self.open_cells = np.zeros((self.width, self.height))
        random.seed(a=seed)
        self.steps = 0
        self.unnecessary_steps = 0

        if self.debug:
            self._assert_invariants()

    def step(self, action):
        first_move = False
        if self.steps == 0:
            first_move = True
            assert self._get_reward() == 0

        if self._get_reward() == 0:
            assert self.steps == 0

        self.steps += 1

        x, y = self._parse_action(action)
        self._open_cell(x, y)

        if first_move and self._game_over() and self.first_move_safe:
            self.reset()
            self.step(action)

        if self.debug and self._game_over():
            print("Game over.")
        if self.debug:
            self._assert_invariants()

        return self._get_state(action)

    def _get_state(self, action):
        observation = self._get_observation()
        reward = self._get_reward()
        done = self._is_done()
        if done and self.window is not None:
            self.window._draw(self._get_observation())
        info = self._get_info(action)
        return observation, reward, done, info


    def reset(self):
        self.open_cells = np.zeros((self.width, self.height))
        self.mines = self._generate_mines()
        self.steps = 0
        self.unnecessary_steps = 0
        if self.debug:
            self._assert_invariants()
        return self._get_observation()

    def legal_actions(self):
        return np.flatnonzero(((self.open_cells - 1) * -1).T)

    def render(self, mode='window'):
        if self.debug:
            self._assert_invariants()

        if mode == "ansi":
            row_strings = []
            for row in self._get_observation().T:
                row_string = ""
                for cell in row:
                    if cell == -2:
                        character = "B"
                    elif cell == -1:
                        character = "x"
                    elif cell == 0:
                        character = "."
                    else:
                        character = str(int(cell))

                    row_string += character
                row_strings.append(row_string)
            return "\n".join(row_strings)

        elif mode == "window" and not self.window:
            from ms_visualizer import MinesweeeperVisualizer
            self.window = MinesweeeperVisualizer()
            self.window.start(self.width, self.height, self.num_mines)
            self.window._draw(self._get_observation())
        elif mode == "window":
            self.window._draw(self._get_observation())

        else:
            print("Did not understand rendering mode. Use any of mode=",
                  self.metadata["render.modes"])

    def close(self):
        if self.window:
            self.window.close(self.pause_after_end)

    def _parse_action(self, action):
        x = action % self.width
        y = action // self.width
        return x, y

    def _open_cell(self, x, y):
        if self.open_cells[x, y]:
            self.unnecessary_steps += 1
        else:
            if self.debug:
                print("Opening cell ({},{})".format(x, y))
            self.open_cells[x, y] = 1
            if self._get_neighbour_mines(x, y) == 0 and self.flood_fill:
                for dx, dy in self.NEIGHBORS:
                    ix, iy = (dx + x, dy + y)
                    if (0 <= ix <= self.width -1 and
                        0 <= iy <= self.height - 1):
                        if (self._get_neighbour_mines(ix, iy) == 0 and
                            not self.open_cells[ix, iy]):
                            self._open_cell(ix, iy)
                        else:
                            self.open_cells[ix, iy] = 1

    def _get_reward(self):
        openable = self.width * self.height - self.num_mines
        open_cells = np.count_nonzero(self.open_cells)
        open_mine = self._game_over()
        punishment = self.unnecessary_steps * self.punishment
        open_cells_reward = (open_cells - punishment) / openable
        return open_cells_reward - open_mine - open_mine / openable

    def _generate_mines(self):
        mines = np.zeros((self.width, self.height))
        mines1d = random.sample(range(self.width * self.height),
                                self.num_mines)
        for coord in mines1d:
            x = coord % self.width
            y = coord // self.width
            mines[x, y] = 1

        return mines

    def _get_observation(self):
        self.open_cells
        observation = np.zeros(self.open_cells.shape)
        for ix, iy in np.ndindex(self.open_cells.shape):
            is_open = self.open_cells[ix, iy]
            is_mine = self.mines[ix, iy]

            if not is_open:
                observation[ix, iy] = -1
            elif is_open and is_mine:
                observation[ix, iy] = -2
            elif is_open:
                observation[ix, iy] = self._get_neighbour_mines(ix, iy)

        return observation

    def _game_over(self):
        logical_and = np.logical_and(self.open_cells, self.mines)
        return np.any(logical_and)

    def _get_neighbour_mines(self, x, y):
        mine_count = 0
        for dx, dy in self.NEIGHBORS:
            ix, iy = (dx + x, dy + y)
            if (0 <= ix <= self.width -1 and
                0 <= iy <= self.height -1 and
                self.mines[ix, iy]):
                mine_count += 1
        return mine_count

    def _get_info(self, action=None):
        return {
            "opened cells": np.count_nonzero(self.open_cells),
            "steps": self.steps,
            "unnecessary steps": self.unnecessary_steps,
            "game over": self._game_over(),
            "mine locations": self.mines.astype(int),
            "opened cell": self._parse_action(action)
        }

    def _assert_invariants(self):
        assert self._get_observation().shape == self.observation_space.shape

        if self._game_over():
            assert -1 <= self._get_reward() < 0, \
                "Game is over, but score is {}".format(self._get_reward())
            assert np.count_nonzero(np.logical_and(self.open_cells,
                                                    self.mines)) == 1, \
                "Game is over, but opened cells is {}".format(
                    np.count_nonzero(np.logical_and(self.open_cells,
                                                    self.mines)))
        else:
            assert 0 <= self._get_reward() < 1, \
                "Game is not over, but score is {}".format(self._get_reward())
            assert np.count_nonzero(np.logical_and(self.open_cells,
                                                    self.mines)) == 0, \
                "Game is not over, but opened mines: {}".format(
                    np.count_nonzero(np.logical_and(self.open_cells,
                                                    self.mines)))

        assert (np.count_nonzero(self.open_cells) == 1 and
                 self._game_over()) == (self._get_reward() == -1), \
            "Game over: {}, mines opened: {}, but score is {}".format(
                self._game_over(),
                np.count_nonzero(self.open_cells),
                self._get_reward())

        assert (np.count_nonzero(self.open_cells) == self.width *
                                                      self.height) == \
                (self._get_reward() == 1), \
            "The game is won ({}), and the score should be 1, " \
            "but the score is {}".format(
                np.count_nonzero(self.open_cells) == self.width * self.height,
                self._get_reward())


        assert (np.count_nonzero(self.open_cells) == 0) == \
                (self._get_reward() == 0), \
            "The game has just started, but the reward is not zero. " \
            "reward:{}".format(self._get_reward())

    def _is_done(self):
        openable = self.width * self.height - self.num_mines
        opened = np.count_nonzero(self.open_cells)
        all_opened = opened == openable
        return self._game_over() or all_opened
