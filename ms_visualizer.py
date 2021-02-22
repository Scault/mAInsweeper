
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'

import pygame
import pygame.locals
import abc
import time
import numpy as np


class Visualizer(abc.ABC):

    @abc.abstractmethod
    def start(self, width, height):
        pass

class MinesweeeperVisualizer(Visualizer):
    TILE_SIZE = 16
    COLOUR_GREY = (189, 189, 189)
    TILES_FILENAME = os.path.join(os.path.dirname(__file__), 'tiles.png')
    TILE_HIDDEN = 9
    TILE_EXPLODED = 10
    TILE_BOMB = 11
    TILE_FLAG = 12
    WINDOW_NAME = 'Minesweeper'

    def __init__(self):
        self.game_width = 0
        self.game_height = 0
        self.num_mines = 0
        self.screen = None
        self.tiles = None

    def start(self, width, height, num_mines):
        self.game_width = width
        self.game_height = height
        self.num_mines = num_mines
        pygame.init()
        pygame.mixer.quit()
        pygame.display.set_caption(self.WINDOW_NAME)
        screen_width = self.TILE_SIZE * self.game_width
        screen_height = self.TILE_SIZE * self.game_height
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        self.screen.fill(self.COLOUR_GREY)
        self.tiles = self._load_tiles()

    def wait(self):
        while 1:
            event = pygame.event.wait()
            if event.type == pygame.locals.KEYDOWN:
                break
            elif event.type == pygame.locals.QUIT:
                pygame.quit()
                break

    def close(self, pause):
        if pause:
            self.wait()
        pygame.quit()

    def _load_tiles(self):
        image = pygame.image.load(self.TILES_FILENAME).convert()
        image_width, image_height = image.get_size()
        tiles = []
        for tile_x in range(0, image_width // self.TILE_SIZE):
            rect = (tile_x * self.TILE_SIZE, 0, self.TILE_SIZE, self.TILE_SIZE)
            tiles.append(image.subsurface(rect))
        return tiles

    def _draw(self, observation):
        openable = self.game_width * self.game_height - self.num_mines
        unique, counts = np.unique(observation, return_counts=True)
        unopened = dict(zip(unique, counts))[-1]
        all_opened = unopened == self.num_mines

        for x in range(self.game_width):
            for y in range(self.game_height):
                if observation[x, y] == -1:
                    if all_opened:
                        tile = self.tiles[self.TILE_BOMB]
                    else:
                        tile = self.tiles[self.TILE_HIDDEN]
                elif observation[x, y] == -2:
                    tile = self.tiles[self.TILE_EXPLODED]
                else:
                    tile = self.tiles[int(observation[x, y])]
                self.screen.blit(tile, (16 * x, 16 * y))
        pygame.display.flip()
