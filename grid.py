import pygame

import constants as c
import random

from image_manager import ImageManager
from primitives import Pose


class Grid:
    def __init__(self, width=1, height=1):
        self.position = Pose((c.WINDOW_WIDTH//2, c.WINDOW_HEIGHT//2))
        self.tiles = [[Tile(self, random.choice([c.TILE_FLOOR] * 2 + [c.TILE_WALL])) for _ in range(width)] for _ in range(height)]
        self.make_edges_walls()
        self.set_tile_poses()
        self.update_tile_sprites()

    def load_from_file(self, file_name):
        with open(file_name) as f:
            lines = f.readlines()
        lines = [line.strip() for line in lines]
        self.tiles = []
        for line in lines:
            tile_line = []
            for char in line:
                tile_line.append(Tile(self, char))
            self.tiles.append(tile_line)
        self.make_edges_walls()
        self.set_tile_poses()
        self.update_tile_sprites()

    def all_tiles(self):
        for row in self.tiles:
            for tile in row:
                yield tile

    def update_tile_sprites(self):
        for tile in self.all_tiles():
            tile.update_surface_from_neighbors()

    def set_tile_poses(self):
        for y, row in enumerate(self.tiles):
            for x, tile in enumerate(row):
                tile.coordinate = x, y

    def make_edges_walls(self):
        for i, row in enumerate(self.tiles):
            for j, tile in enumerate(row):
                if j == 0 or j == len(row) - 1 or i == 0 or i == len(self.tiles) - 1:
                    row[j] = Tile(self, c.TILE_WALL)

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

    def tile_coordinate_to_position(self, x, y):
        x0 = -self.width_pixels()//2 + c.TILE_WIDTH//2 + self.position.x
        y0 = -self.height_pixels()//2 + c.TILE_HEIGHT//2 + self.position.y
        x_pos = x0 + x * c.TILE_WIDTH
        y_pos = y0 + y * c.TILE_HEIGHT
        return Pose((x_pos, y_pos))

    def position_to_tile_coordinate(self, x_pos, y_pos):
        x0 = -self.width_pixels()//2 + c.TILE_WIDTH//2 + self.position.x
        y0 = -self.height_pixels()//2 + c.TILE_HEIGHT//2 + self.position.y
        x = int((x_pos - x0)/c.TILE_WIDTH)
        y = int((y_pos - y0)/c.TILE_WIDTH)
        return x, y

    def width_pixels(self):
        return len(self.tiles[0]) * c.TILE_WIDTH

    def height_pixels(self):
        return len(self.tiles) * c.TILE_HEIGHT

    def get_interior_bounds(self):
        x1 = ((len(self.tiles[0]) - 2) * c.TILE_WIDTH)//2 + self.position.x
        x0 = -((len(self.tiles[0]) - 2) * c.TILE_WIDTH)//2 + self.position.x
        y1 = ((len(self.tiles) - 2) * c.TILE_HEIGHT)//2 + self.position.y
        y0 = -((len(self.tiles) - 2) * c.TILE_HEIGHT)//2 + self.position.y
        return x0, x1, y0, y1

    def nearby_tiles(self, pose, reach_tiles = 2):
        x, y = self.position_to_tile_coordinate(*pose.get_position())
        x += 1
        y += 1
        x_min = max(0, x - reach_tiles)
        y_min = max(0, y - reach_tiles)
        x_max = min(len(self.tiles[0]), x + reach_tiles)
        y_max = min(len(self.tiles), y + reach_tiles)
        for x_c in range(x_min, x_max):
            for y_c in range(y_min, y_max):
                yield x_c, y_c

    def get_tile(self, x, y):
        return self.tiles[y][x]

class Tile:
    FLOOR = None

    def __init__(self, grid, tile_type=c.TILE_WALL):
        self.grid = grid
        self.tile_type = tile_type
        self.surface = pygame.Surface(c.TILE_SIZE)
        if (tile_type == c.TILE_FLOOR):
            self.surface.fill((135, 200, 120))
        elif tile_type == c.TILE_WALL:
            self.surface.fill(c.BLACK)
        elif tile_type == c.TILE_SPAWN:
            self.surface.fill(c.LIGHT_GRAY)
        else:
            self.surface.fill(c.GRAY)
        self.coordinate = (0, 0)

        self.highlighted = False
        self.collidable = self.tile_type in [c.TILE_WALL]
        if self.FLOOR == None:
            Tile.FLOOR = "Don't question it!"
            Tile.FLOOR = Tile(self.grid, c.TILE_FLOOR)

    def update_surface_from_neighbors(self):
        if self.tile_type == c.TILE_WALL:
            path = ""
            neighbors = [[Tile(self.grid, c.TILE_WALL) for _ in range(3)] for _ in range(3)]
            for x in [-1, 0, 1]:
                for y in [-1, 0, 1]:
                    x_n = self.coordinate[0] + x
                    y_n = self.coordinate[1] + y
                    if x_n <= 0 or x_n >= len(self.grid.tiles[0]):
                        continue
                    if y_n <= 0 or y_n >= len(self.grid.tiles):
                        continue
                    neighbors[y+1][x+1] = self.grid.tiles[y_n][x_n]
            if neighbors[2][1].collidable and neighbors[1][2].collidable and neighbors[1][0].collidable and not neighbors[0][1].collidable:
                path = "border_bottom.png"
            elif neighbors[2][1].collidable and neighbors[1][2].collidable and neighbors[1][0].collidable and neighbors[0][1].collidable:
                if not neighbors[0][2].collidable:
                    path = "border_in_bl.png"
                elif not neighbors[0][0].collidable:
                    path = "border_in_br.png"
                elif not neighbors[2][2].collidable:
                    path = "border_in_tl.png"
                elif not neighbors[2][0].collidable:
                    path = "border_in_tr.png"
            elif neighbors[2][1].collidable and not neighbors[1][2].collidable and neighbors[1][0].collidable and neighbors[0][1].collidable:
                path = "border_left.png"
            elif not neighbors[2][1].collidable and neighbors[1][2].collidable and not neighbors[1][0].collidable and neighbors[0][1].collidable:
                path = "border_out_bl.png"
            elif not neighbors[2][1].collidable and not neighbors[1][2].collidable and neighbors[1][0].collidable and neighbors[0][1].collidable:
                path = "border_out_br.png"
            elif neighbors[2][1].collidable and neighbors[1][2].collidable and not neighbors[1][0].collidable and not neighbors[0][1].collidable:
                path = "border_out_tl.png"
            elif neighbors[2][1].collidable and not neighbors[1][2].collidable and neighbors[1][0].collidable and not neighbors[0][1].collidable:
                path = "border_out_tr.png"
            elif neighbors[2][1].collidable and neighbors[1][2].collidable and not neighbors[1][0].collidable and neighbors[0][1].collidable:
                path = "border_right.png"
            elif not neighbors[2][1].collidable and neighbors[1][2].collidable and neighbors[1][0].collidable and neighbors[0][1].collidable:
                path = "border_top.png"
            if path:
                self.surface = pygame.transform.scale(ImageManager.load(f"assets/images/{path}"), c.TILE_SIZE)

        pass

    def update(self, dt, events):
        self.highlighted = False
        pass

    def draw(self, surface, offset=(0, 0)):
        if (self.tile_type != c.TILE_FLOOR):
            self.FLOOR.draw(surface, offset)

        x = offset[0] - c.TILE_WIDTH//2
        y = offset[1] - c.TILE_WIDTH//2
        surface.blit(self.surface, (x, y))

        if self.highlighted:
            pygame.draw.rect(surface, (255, 255, 0), (x, y, c.TILE_WIDTH, c.TILE_HEIGHT), 1)

    def collide_with(self, bee):
        if not self.collidable:
            return False
        position = self.grid.tile_coordinate_to_position(*self.coordinate)
        diff = bee.pose - position
        mag = diff.magnitude()
        if mag > c.TILE_WIDTH * 1.5 + bee.radius:
            return False

        result = False
        for corner_position in ((-1, -1), (-1, 1), (1, -1), (1, 1)):
            x = corner_position[0] * c.TILE_WIDTH//2 + position.x
            y = corner_position[1] * c.TILE_HEIGHT//2 + position.y
            result = bee.nudge_from_point(Pose((x, y)))

        if abs(bee.pose.x - position.x) < c.TILE_WIDTH//2 and abs(bee.pose.y - position.y) < bee.radius + c.TILE_HEIGHT//2:
            sign = -1 if bee.pose.y < position.y else 1
            bee.pose.y = position.y + (bee.radius + c.TILE_HEIGHT//2) * sign
            result = True
        if abs(bee.pose.y - position.y) < c.TILE_HEIGHT//2 and abs(bee.pose.x - position.x) < bee.radius + c.TILE_WIDTH//2:
            sign = -1 if bee.pose.x < position.x else 1
            bee.pose.x = position.x + (bee.radius + c.TILE_WIDTH//2) * sign
            result = True

        return result