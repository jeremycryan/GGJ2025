import random
import time

import pygame

from bee import Bee
from grid import Grid
import constants as c
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
        self.since_freeze = 0

    def load(self):
        self.grid = Grid(*c.GRID_SIZE)
        self.grid.load_from_file(f"assets/maps/level_{random.choice([1, 2, 3, 4, 5])}.txt")
        self.players = [Bee(self), Bee(self, Bee.BeeControl(pygame.K_n, pygame.K_m))]
        self.particles = []
        pass

    def freeze(self, time):
        self.since_freeze = min(-time, self.since_freeze)

    def update(self, dt, events):
        self.since_freeze += dt
        for particle in self.particles:
            particle.update(dt, events)
        self.particles = [particle for particle in self.particles if not particle.destroyed]

        if (self.since_freeze < 0):
            fade = 0.1
            if self.since_freeze < -fade:
                dt *= 0.01
            else:
                dt *= 0.01 + 0.99 * (1 - self.since_freeze/-fade)


        self.grid.update(dt, events)
        for player in self.players:
            player.early_update(dt, events)
        for player in self.players:
            player.update(dt, events)
        pass

    def draw(self, surface, offset=(0, 0)):
        surface.fill((0, 0, 0))
        self.grid.draw(surface, offset)
        for player in self.players:
            player.draw(surface, offset)
        for particle in self.particles:
            particle.draw(surface, offset)

    def next_frame(self):
        return Frame(self.game)

