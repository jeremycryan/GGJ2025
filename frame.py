import time

import pygame

from bee import Bee
from grid import Grid
from image_manager import ImageManager
from sound_manager import SoundManager


class Frame:
    def __init__(self, game):
        self.game = game
        self.done = False

    def load(self):
        pass

    def update(self, dt, events):
        pass

    def draw(self, surface, offset=(0, 0)):
        surface.fill((128, 128, 128))

    def next_frame(self):
        return Frame(self.game)

class MainFrame:
    def __init__(self, game):
        self.game = game
        self.done = False

    def load(self):
        self.grid = Grid(19, 12)
        self.players = [Bee()]
        pass

    def update(self, dt, events):
        self.grid.update(dt, events)
        for player in self.players:
            player.update(dt, events)
        pass

    def draw(self, surface, offset=(0, 0)):
        surface.fill((128, 128, 128))
        self.grid.draw(surface, offset)
        for player in self.players:
            player.draw(surface, offset)

    def next_frame(self):
        return Frame(self.game)

