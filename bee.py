import pygame
from primitives import *
import constants as c

from image_manager import ImageManager

class Bee:
    TOP_SPEED = 400
    ACCELERATION = 700
    ROTATION = 270
    FLIP_SPEED = 6
    UNFLIP_SPEED = 2.5
    BRAKE_COOLDOWN = 1.25

    def __init__(self, control=None):
        self.control = control if control is not None else Bee.BeeControl()
        self.pose = Pose((c.GRID_WIDTH_PIXELS //2, c.GRID_HEIGHT_PIXELS //2))
        self.speed = 0

        self.braking = False
        self.start_brake_pose = self.pose.copy()
        self.flipped = 0
        self.since_brake = 0

        self.surface = ImageManager.load("assets/images/bee.png")

    def start_brake(self):
        self.start_brake_pose = self.pose.copy()
        self.braking = True
        self.since_brake = 0
        self.speed *= 2

    def stop_brake(self):
        self.flipped = 0
        self.pose.angle += 180
        self.braking = False

    def update(self, dt, events):
        self.update_movement(dt, events)

    def update_movement(self, dt, events):
        pressed = pygame.key.get_pressed()

        velocity = Pose((0, 0))

        if pressed[self.control.flip] and not self.braking:
            self.start_brake()

        if not self.braking:
            self.flipped -= self.UNFLIP_SPEED * dt
            if self.flipped < 0:
                self.flipped = 0
            if pressed[self.control.turn_right]:
                self.pose.angle += self.ROTATION * dt
            else:
                self.pose.angle -= self.ROTATION * dt

            if self.speed < self.TOP_SPEED:
                self.speed += dt * self.ACCELERATION
                if (self.speed > self.TOP_SPEED):
                    self.speed = self.TOP_SPEED

            direction = self.pose.get_unit_vector()
            velocity = direction * self.speed

        if self.braking:
            self.flipped += self.FLIP_SPEED * dt
            if (self.flipped > 1):
                self.flipped = 1

            if self.speed > 0:
                self.speed *= 0.05**dt

            self.since_brake += dt
            if self.since_brake > self.BRAKE_COOLDOWN:
                if not pressed[self.control.flip]:
                    self.stop_brake()

            velocity = self.start_brake_pose.get_unit_vector() * self.speed

        self.pose += velocity * dt

    def draw(self, surface, offset=(0, 0)):
        rotated = pygame.transform.rotate(self.surface, self.pose.angle + self.flipped * 180)
        x = self.pose.x + offset[0] - rotated.get_width()//2
        y = self.pose.y + offset[1] - rotated.get_height()//2

        surface.blit(rotated, (x, y))

    class BeeControl:
        def __init__(self):
            self.turn_right = pygame.K_z
            self.flip = pygame.K_x

