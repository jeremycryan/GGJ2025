import pygame

import constants as c
import random
from primitives import Pose


class Grid:
    def __init__(self, width=1, height=1):
        self.position = Pose((c.WINDOW_WIDTH//2, c.WINDOW_HEIGHT//2))
        self.tiles = [[Tile(random.choice([c.TILE_WALL] + 8 * [c.TILE_FLOOR])) for _ in range(width)] for _ in range(height)]
        self.make_edges_walls()

    def make_edges_walls(self):
        for i, row in enumerate(self.tiles):
            for j, tile in enumerate(row):
                if j == 0 or j == len(row) - 1 or i == 0 or i == len(self.tiles) - 1:
                    row[j] = Tile(c.TILE_WALL)

    def update(self, dt, events):
        for row in self.tiles:
            for tile in row:
                tile.update(dt, events)

    def draw(self, surface, offset=(0, 0)):
        x0 = offset[0] - self.width_pixels()//2 + c.TILE_WIDTH//2 + self.position.x
        y0 = offset[1] - self.height_pixels()//2 + c.TILE_HEIGHT//2 + self.position.y
        y = y0
        for row in self.tiles:
            x = x0
            for tile in row:
                tile.draw(surface, (x, y))
                x += c.TILE_WIDTH
            y += c.TILE_HEIGHT

    def width_pixels(self):
        return len(self.tiles[0]) * c.TILE_WIDTH

    def height_pixels(self):
        return len(self.tiles) * c.TILE_HEIGHT


class Tile:
    def __init__(self, tile_type=c.TILE_WALL):
        self.tile_type = tile_type
        self.surface = pygame.Surface(c.TILE_SIZE)
        if (tile_type == c.TILE_FLOOR):
            self.surface.fill(c.WHITE)
        elif tile_type == c.TILE_WALL:
            self.surface.fill(c.BLACK)
        else:
            self.surface.fill(c.GRAY)

    def update(self, dt, events):
        pass

    def draw(self, surface, offset=(0, 0)):
        x = offset[0] - c.TILE_WIDTH//2
        y = offset[1] - c.TILE_WIDTH//2
        surface.blit(self.surface, (x, y))
