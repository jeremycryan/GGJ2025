import math

import pygame

from bee import Bee
from image_manager import ImageManager
import constants as c
from primitives import Pose


class PlayerPlacard:

    def __init__(self, position=(0, 0), player=1, frame=None):
        self.frame = frame
        self.player = player
        self.name = f"P{player}"
        self.score = self.frame.game.scores[player]
        self.control = Bee.BeeControl(*c.P1_CONTROL)
        if player == 2:
            self.control = Bee.BeeControl(*c.P2_CONTROL)
        if player == 3:
            self.control = Bee.BeeControl(*c.P3_CONTROL)
        if player == 4:
            self.control = Bee.BeeControl(*c.P4_CONTROL)

        self.name_font = pygame.font.SysFont("sans", 60, True)
        self.score_font = pygame.font.SysFont("sans", 25, False)
        self.controls_font = pygame.font.SysFont("sans", 30, False)

        self.position = Pose(position)

        self.surface = self.generate_surface()

        self.bounce_amt = 0
        self.since_bounce = 999


    def gain_point(self):
        self.score += 1
        self.surface = self.generate_surface()
        self.bounce()

    def regenerate_surface(self):
        self.surface = self.generate_surface()

    def generate_surface(self):
        base = ImageManager.load_copy("assets/images/player_placard.png")

        name = self.name_font.render(self.name, False, c.WHITE)
        control = self.controls_font.render(f"{pygame.key.name(self.control.turn_right)}, {pygame.key.name(self.control.flip)}".upper(), False, c.WHITE)
        score = self.score_font.render(f"Score: {self.score}", False, c.WHITE)

        base.blit(name, (base.get_width()//2 - name.get_width()//2, 20))
        base.blit(control, (base.get_width()//2 - control.get_width()//2, 80))
        base.blit(score, (base.get_width()//2 - score.get_width()//2, 240))

        color = c.P1_COLOR

        if self.player == 2:
            color = c.P2_COLOR
        if self.player == 3:
            color = c.P3_COLOR
        if self.player == 4:
            color = c.P4_COLOR

        bee = Bee(self.frame, None, color, position=(0, 0))

        bee.draw(base, (base.get_width()//2, base.get_height()//2 + 25))

        #base.blit(bee, (base.get_width()//2 - bee.get_width()//2, base.get_height()//2 - bee.get_height()//2 + 25))

        return base

    def bounce(self):
        self.since_bounce = 0
        self.bounce_amt = 10

    def update(self, dt, events):

        self.bounce_amt *= 0.1**dt
        self.bounce_amt -= 2*dt
        if self.bounce_amt < 0:
            self.bounce_amt = 0
        self.since_bounce += dt
        pass

    def draw(self, surface, offset=(0, 0)):
        x = self.position.x + offset[0] - self.surface.get_width()//2
        y = self.position.y + offset[1] - self.surface.get_height()//2

        y += math.cos(self.since_bounce * 25) * self.bounce_amt

        surface.blit(self.surface, (x, y))
