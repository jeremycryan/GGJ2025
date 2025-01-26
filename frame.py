import random
import time

import pygame

from Button import Button
from bee import Bee
from grid import Grid
import constants as c
from image_manager import ImageManager
from player_placard import PlayerPlacard
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

class MainFrame(Frame):
    def __init__(self, game):
        super().__init__(game)
        self.since_freeze = 0

    def load(self):
        self.grid = Grid(*c.GRID_SIZE)
        self.grid.load_from_file(f"assets/maps/level_{random.choice([1, 2, 3, 4, 5])}.txt")
        self.players = [Bee(self, Bee.BeeControl(*c.P1_CONTROL), color=c.P1_COLOR, position=self.grid.spawn_position(1)),
                        Bee(self, Bee.BeeControl(*c.P2_CONTROL), color=c.P2_COLOR, position=self.grid.spawn_position(2)),
                        Bee(self, Bee.BeeControl(*c.P3_CONTROL), color=c.P3_COLOR, position=self.grid.spawn_position(3)),
                        Bee(self, Bee.BeeControl(*c.P4_CONTROL), color=c.P4_COLOR, position=self.grid.spawn_position(4))]
        self.players = self.players[:self.game.player_count]
        self.particles = []
        self.round_over = False
        self.black = pygame.Surface(c.WINDOW_SIZE)
        self.black.fill((c.BLACK))
        self.darken = 1
        self.freeze(1.25)
        pass

    def freeze(self, time):
        self.since_freeze = min(-time, self.since_freeze)

    def update(self, dt, events):
        self.since_freeze += dt
        for particle in self.particles:
            particle.update(dt, events)
        self.particles = [particle for particle in self.particles if not particle.destroyed]

        if not self.round_over:
            self.darken -= 3*dt
            if self.darken < 0:
                self.darken = 0
        else:
            self.darken += 2*dt
            if (self.darken > 1):
                self.darken = 1
                for player in self.players:
                    if player.color == c.P1_COLOR:
                        self.game.store_last_winner(1)
                    elif player.color == c.P2_COLOR:
                        self.game.store_last_winner(2)
                    elif player.color == c.P3_COLOR:
                        self.game.store_last_winner(3)
                    elif player.color == c.P4_COLOR:
                        self.game.store_last_winner(4)
                    else:
                        self.game.store_last_winner(None)
                self.done = True

        if (self.since_freeze < 0):
            fade = 0.1
            if self.since_freeze < -fade:
                dt *= 0.01
            else:
                dt *= 0.01 + 0.99 * (1 - self.since_freeze/-fade)

        self.grid.update(dt, events)
        for player in self.players:
            player.early_update(dt, events)
        self.players = [player for player in self.players if (player.inactive == False)]
        for player in self.players:
            player.update(dt, events)
        if len([player for player in self.players if not player.dead]) <= 1:
            for player in self.players:
                if not player.dead and not player.inactive:
                    player.invulnerable = True
                    player.controllable = False
            self.round_end()
        pass

    def round_end(self):
        if self.round_over:
            return
        self.round_over = True
        self.darken = -4



    def draw(self, surface, offset=(0, 0)):
        surface.fill((0, 0, 0))
        self.grid.draw(surface, offset)
        for player in self.players:
            player.draw(surface, offset)
        for particle in self.particles:
            particle.draw(surface, offset)

        if (self.darken > 0):
            self.black.set_alpha(self.darken * 255)
            surface.blit(self.black, (0, 0))

    def next_frame(self):
        return ScoreFrame(self.game)

class MenuFrame(Frame):
    def load(self):
        self.buttons = [
            Button(
                ImageManager.load_copy("assets/images/button_back.png"),
                pos=(200, c.WINDOW_HEIGHT * 0.37),
                text="2 players",
                on_click=self.start_2_player,
                hover_surf=ImageManager.load_copy("assets/images/button_back_hover.png")
            ),
            Button(
                ImageManager.load_copy("assets/images/button_back.png"),
                pos=(200, c.WINDOW_HEIGHT * 0.5),
                text="3 players",
                on_click=self.start_3_player,
                hover_surf=ImageManager.load_copy("assets/images/button_back_hover.png")
            ),
            Button(
                ImageManager.load_copy("assets/images/button_back.png"),
                pos=(200, c.WINDOW_HEIGHT * 0.63),
                text="4 players",
                on_click=self.start_4_player,
                hover_surf=ImageManager.load_copy("assets/images/button_back_hover.png")
            ),
        ]

    def update(self, dt, events):
        for button in self.buttons:
            button.update(dt, events)

    def draw(self, surface, offset=(0, 0)):
        surface.fill((0, 0, 0))
        for button in self.buttons:
            button.draw(surface, *offset)


    def start_2_player(self):
        self.game.player_count = 2
        self.end_frame()

    def start_3_player(self):
        self.game.player_count = 3
        self.end_frame()

    def start_4_player(self):
        self.game.player_count = 4
        self.end_frame()

    def end_frame(self):
        self.done = True

    def next_frame(self):
        return ScoreFrame(self.game)

class ScoreFrame(Frame):
    def load(self):
        y = c.WINDOW_HEIGHT//2
        self.age = 0
        self.incremented = False

        self.placards = []
        x = (self.game.player_count - 1) * -0.105
        for i in range(self.game.player_count):
            self.placards.append(PlayerPlacard((c.WINDOW_WIDTH//2 + c.WINDOW_WIDTH * x, y), i+1, self))
            x += 0.21

    def update(self, dt, events):
        for placard in self.placards:
            placard.update(dt, events)
        self.age += dt
        if self.age > 5:
            self.done = True
        if self.age > 2 and not self.incremented:
            self.incremented = True
            if (self.game.last_winner != None):
                self.game.give_point(self.game.last_winner)
                self.placards[self.game.last_winner - 1].bounce()
                self.placards[self.game.last_winner - 1].score += 1
                self.placards[self.game.last_winner - 1].regenerate_surface()

    def draw(self, surface, offset=(0, 0)):
        surface.fill(c.BLACK)
        for placard in self.placards:
            placard.draw(surface, offset)

    def next_frame(self):
        return MainFrame(self.game)