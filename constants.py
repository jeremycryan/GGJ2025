import pygame


WINDOW_WIDTH = 960
WINDOW_HEIGHT = 540
WINDOW_SIZE = WINDOW_WIDTH, WINDOW_HEIGHT

SCALED_WINDOW_WIDTH = 1920
SCALED_WINDOW_HEIGHT = 1080
SCALED_WINDOW_SIZE = SCALED_WINDOW_WIDTH, SCALED_WINDOW_HEIGHT

CAPTION = "Bubble Bee 2D"
FRAMERATE = 100

TILE_FLOOR = "."
TILE_WALL = "X"
TILE_SPAWN_P1 = "1"
TILE_SPAWN_P2 = "2"
TILE_SPAWN_P3 = "3"
TILE_SPAWN_P4 = "4"

TILE_WIDTH = 28
TILE_HEIGHT = 28
TILE_SIZE = TILE_WIDTH, TILE_HEIGHT

WHITE = 255, 255, 255
BLACK = 0, 0, 0
BLUE = 0, 0, 255
RED = 255, 0, 0
GREEN = 0, 255, 0
CYAN = 0, 255, 255
MAGENTA = 255, 0, 255
YELLOW = 255, 255, 0
GRAY = 128, 128, 128
LIGHT_GRAY = 200, 200, 200

GRID_WIDTH = 30
GRID_HEIGHT = 17
GRID_SIZE = GRID_WIDTH, GRID_HEIGHT
GRID_WIDTH_PIXELS = GRID_WIDTH * TILE_WIDTH
GRID_HEIGHT_PIXELS = GRID_HEIGHT * TILE_HEIGHT

ORIGIN = (WINDOW_WIDTH - GRID_WIDTH_PIXELS)//2, (WINDOW_HEIGHT - GRID_HEIGHT_PIXELS)//2

UP = 0
LEFT = 1
DOWN = 2
RIGHT = 3

P1_CONTROL = pygame.K_q, pygame.K_w
P2_CONTROL = pygame.K_o, pygame.K_p
P3_CONTROL = pygame.K_z, pygame.K_x
P4_CONTROL = pygame.K_n, pygame.K_m

P1_COLOR = 255, 40, 80
P2_COLOR = 80, 40, 255
P3_COLOR = 0, 140, 50
P4_COLOR = 200, 150, 0

CHARS = " QWERTYUIOPASDFGHJKLZXCVBNMqwertyuiopasdfghjklzxcvbnm1234567890,.<>;"