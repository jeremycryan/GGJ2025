import math

import pygame

import frame as f
import constants as c
import sys

from sound_manager import SoundManager
from image_manager import ImageManager
from primitives import Pose
import asyncio


class Game:
    def __init__(self):
        pygame.init()
        SoundManager.init()
        ImageManager.init()
        self.small_screen = pygame.Surface(c.WINDOW_SIZE)
        self.screen = pygame.display.set_mode(c.SCALED_WINDOW_SIZE)

        self.clock = pygame.time.Clock()
        pygame.mixer.init()

        self.shake_amp = 0
        self.since_shake = 999

        pygame.display.set_caption(f"{c.CAPTION}")

        self.fps_font = pygame.font.SysFont("monospace", 20)
        self.fps_log = [0] * 100

        self.scores = {1:0, 2:0, 3:0, 4:0}
        self.last_winner = None
        self.player_count = 3

        asyncio.run(self.main())

    def store_last_winner(self, player):
        self.last_winner = player

    def give_point(self, player):
        self.scores[player] += 1

    def shake(self, amt=15):
        self.shake_amp = amt
        self.since_shake = 0

    def get_shake_offset(self):
        magnitude = math.cos(self.since_shake * 60) * self.shake_amp
        direction = Pose((1, 1))
        if abs(magnitude) < 1:
            magnitude = 0
        return direction * magnitude

    async def main(self):
        current_frame = f.MenuFrame(self)
        current_frame.load()
        self.clock.tick(c.FRAMERATE)

        while True:
            dt, events = self.get_events()
            self.fps_log = self.fps_log[1:] + [1 / dt]
            fps = sum(self.fps_log)/100
            fps_text = self.fps_font.render(f"FPS: {int(fps)}",True,(255, 255, 255))

            if dt == 0:
                dt = 1/100000
            if dt > 0.05:
                dt = 0.05
            current_frame.update(dt, events)
            current_frame.draw(self.small_screen, self.get_shake_offset().get_position())
            scaled = pygame.transform.scale(self.small_screen, c.SCALED_WINDOW_SIZE)
            self.screen.blit(scaled, (0, 0))
            self.screen.blit(fps_text, (0, 0))
            pygame.display.flip()
            await asyncio.sleep(0)

            if current_frame.done:
                current_frame = current_frame.next_frame()
                current_frame.load()

    def get_events(self):

        dt = self.clock.tick(c.FRAMERATE)/1000


        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F4:
                    pygame.display.toggle_fullscreen()

        self.since_shake += dt
        self.shake_amp *= 0.006 ** dt

        return dt, events


if __name__ == "__main__":
    Game()
