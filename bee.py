import pygame

from particle import Pop
from primitives import *
import constants as c
import random

from image_manager import ImageManager

class Bee:
    TOP_SPEED = 300
    ACCELERATION = 500
    ROTATION = 215
    FLIP_SPEED = 13
    UNFLIP_SPEED = 2.5
    BRAKE_COOLDOWN = 1.1
    STINGER_LENGTH = 45
    DASH_MULTIPLIER = 2.6
    BRAKE_AMOUNT = 0.03

    def __init__(self, frame, control=None, color=None, position = None):
        self.control = control if control is not None else Bee.BeeControl()
        if position == None:
            position = (c.GRID_WIDTH_PIXELS //2 + random.random() * 800 - 400,
                          c.GRID_HEIGHT_PIXELS //2 + random.random() * 200 - 100)

        self.pose = Pose(position,
                         random.random() * 360)
        self.speed = 0

        self.braking = False
        self.start_brake_pose = self.pose.copy()
        self.flipped = 0
        self.since_brake = 0

        self.surface = ImageManager.load_copy("assets/images/bee.png")
        self.radius = 24
        self.frame = frame
        if color is not None:
            self.color = color
        else:
            self.color = [random.random() * 55 + 200, random.random() * 255, 30]
            random.shuffle(self.color)

        self.surface = Bee.get_bee_surf(self.color)

        self.age = 0
        self.dead = False
        self.inactive = False
        self.invulnerable = False
        self.controllable = True
        self.already_bounced_with = []

        self.shadow = pygame.Surface((self.radius * 2, self.radius * 2))
        self.shadow.fill(c.WHITE)
        pygame.draw.circle(self.shadow, c.BLACK, (self.radius, self.radius), self.radius)
        self.shadow.set_colorkey(c.WHITE)
        self.shadow.set_alpha(50)

        self.debug = False

    @staticmethod
    def get_bee_surf(color):
        surface = ImageManager.load_copy("assets/images/bee.png")
        tint = surface.copy()
        tint.fill(color)
        surface.blit(tint, (0, 0), special_flags=pygame.BLEND_MULT)
        surface.set_colorkey(surface.get_at((0, 0)))
        return surface

    def stinger_location(self):
        heading = Pose((0, 0), self.pose.angle + 180 * self.flipped + 180)
        stinger_vector = heading.get_unit_vector() * self.STINGER_LENGTH
        return self.pose + stinger_vector

    def collides_with_point(self, pose):
        if (self.pose - pose).magnitude() < self.radius:
            return True
        return False

    def check_stung_bees(self, others):
        stung = []
        for bee in others:
            if bee == self:
                continue
            if bee.collides_with_point(self.stinger_location()):
                stung.append(bee)
        for bee in stung:
            self.sting(bee)

    def sting(self, other):
        if not self.inactive:
            self.speed = -abs(self.speed)
            other.die()

    def die(self):
        if not self.dead and not self.invulnerable:
            self.frame.particles.append(Pop(self.pose.get_position(), duration = 1))
            self.frame.game.shake(15)
            self.frame.freeze(0.7)
            self.dead = True

    def start_brake(self):
        self.start_brake_pose = self.pose.copy()
        self.braking = True
        self.since_brake = 0
        self.speed *= self.DASH_MULTIPLIER

    def stop_brake(self):
        self.flipped = 0
        self.pose.angle += 180
        self.braking = False

    def early_update(self, dt, events):
        if self.dead:
            self.inactive = True
        self.already_bounced_with = []

    def update(self, dt, events):
        self.age += dt
        self.update_movement(dt, events)
        self.update_collision(dt, events)

    def update_collision(self, dt, events):
        if self.inactive:
            return

        bounds = self.frame.grid.get_interior_bounds()
        if (self.pose.x - self.radius < bounds[0]):
            self.pose.x = bounds[0] + self.radius
        if (self.pose.x + self.radius > bounds[1]):
            self.pose.x = bounds[1] - self.radius
        if (self.pose.y - self.radius < bounds[2]):
            self.pose.y = bounds[2] + self.radius
        if (self.pose.y + self.radius > bounds[3]):
            self.pose.y = bounds[3] - self.radius

        self.check_stung_bees(self.frame.players)
        self.check_bounced_bees(self.frame.players)

        for tile in self.frame.grid.nearby_tiles(self.pose, 2):
            if self.frame.grid.get_tile(*tile).collide_with(self):
                pass#self.frame.game.shake(2)

    def check_bounced_bees(self, bees):
        for bee in bees:
            if bee == self:
                continue
            if bee.inactive:
                continue
            if bee in self.already_bounced_with:
                continue
            if (bee.pose - self.pose).magnitude() < bee.radius + self.radius:
                self.bounce(bee)

    def bounce(self, other):
        if self.inactive or other.inactive:
            return

        self.speed *= -0.75
        other.speed *= -0.75

        diff = other.pose - self.pose
        overlap = other.radius + self.radius - diff.magnitude()
        nudge = diff * overlap * (1/diff.magnitude()) * (0.5)
        nudge.angle = 0
        self.pose -= nudge
        other.pose += nudge

        self.already_bounced_with.append(other)
        other.already_bounced_with.append(self)

        self.frame.game.shake(3)

    def nudge_from_point(self, point_pose):
        diff = self.pose - point_pose
        diff_mag = diff.magnitude()
        if (diff_mag > self.radius):
            return False
        nudge_amount = self.radius - diff_mag
        diff.scale_to(nudge_amount)
        diff.angle = 0
        self.pose += diff
        return True

    def update_movement(self, dt, events):
        pressed = pygame.key.get_pressed()

        velocity = Pose((0, 0))

        if pressed[self.control.flip] and self.controllable and not self.braking:
            self.start_brake()

        if not self.braking:
            self.flipped -= self.UNFLIP_SPEED * dt
            if self.flipped < 0:
                self.flipped = 0
            if pressed[self.control.turn_right] and self.controllable:
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

            self.speed *= self.BRAKE_AMOUNT**dt

            self.since_brake += dt
            if self.since_brake > self.BRAKE_COOLDOWN:
                if not pressed[self.control.flip] or not self.controllable:
                    self.stop_brake()

            velocity = self.start_brake_pose.get_unit_vector() * self.speed

        self.pose += velocity * dt

    def draw(self, surface, offset=(0, 0)):
        if self.inactive:
            return

        surface.blit(self.shadow, (self.pose.x + offset[0] - self.radius, self.pose.y + offset[1] + 12 - self.radius))

        stretch_amt = 1 + 0.1 * self.speed / self.TOP_SPEED
        w = self.surface.get_width() * stretch_amt
        h = self.surface.get_height() / stretch_amt
        stretched = pygame.transform.scale(self.surface, (w, h))

        rotated = pygame.transform.rotate(stretched, self.pose.angle + self.flipped * 180)
        x = self.pose.x + offset[0] - rotated.get_width()//2
        y = self.pose.y + offset[1] - rotated.get_height()//2

        surface.blit(rotated, (x, y))

        if self.debug:
            xs = self.stinger_location().x + offset[0]
            ys = self.stinger_location().y + offset[1]
            pygame.draw.circle(surface, (255, 255, 255), (xs, ys), 3)
            pygame.draw.circle(surface, (255, 255, 255), (self.pose.x + offset[0], self.pose.y + offset[1]), self.radius, 2)



    class BeeControl:
        def __init__(self, turn_right=pygame.K_q, flip=pygame.K_w):
            self.turn_right = turn_right
            self.flip = flip

