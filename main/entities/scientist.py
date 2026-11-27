import math
import random

import pygame

from entities.character_sprite import load_character_frame


class Scientist(pygame.sprite.Sprite):
    def __init__(self, pos, tilemap):
        super().__init__()
        self.image = load_character_frame("Siencentist.png", (32, 32), (32, 32))
        self.rect = self.image.get_rect(midbottom=pos)
        self.hitbox = pygame.Rect(0, 0, 20, 8)
        self.hitbox.midbottom = self.rect.midbottom
        self.pos = pygame.Vector2(self.hitbox.midbottom)
        self.home = pygame.Vector2(pos)
        self.tilemap = tilemap
        self.speed = 180
        self.health = 1
        self.tased = False
        self.target = self._choose_target()
        self.direction_time = random.uniform(0.2, 0.6)

    def _choose_target(self):
        angle = random.uniform(0, math.tau)
        distance = random.uniform(40, 200)
        return self.home + pygame.Vector2(distance, 0).rotate_rad(angle)

    def take_damage(self, damage):
        self.health = max(0, self.health - damage)
        if self.health == 0:
            self.tased = True

    def stun(self, duration):
        self.tased = True

    def update(self, dt):
        if self.tased:
            return

        self.direction_time -= dt
        offset = self.target - self.pos
        if self.direction_time <= 0 or offset.length_squared() < 100:
            self.target = self._choose_target()
            self.direction_time = random.uniform(0.2, 0.6)
            offset = self.target - self.pos

        if offset.length_squared() == 0:
            return

        motion = offset.normalize() * min(offset.length(), self.speed * dt)
        self.pos.x += motion.x
        self.hitbox.x = round(self.pos.x - self.hitbox.width / 2)
        for rect in self.tilemap.collision_rects:
            if self.hitbox.colliderect(rect):
                self.hitbox.right = rect.left if motion.x > 0 else self.hitbox.right
                if motion.x < 0:
                    self.hitbox.left = rect.right
                self.pos.x = self.hitbox.centerx
                self.target = self._choose_target()

        self.pos.y += motion.y
        self.hitbox.y = round(self.pos.y - self.hitbox.height)
        for rect in self.tilemap.collision_rects:
            if self.hitbox.colliderect(rect):
                if motion.y > 0:
                    self.hitbox.bottom = rect.top
                elif motion.y < 0:
                    self.hitbox.top = rect.bottom
                self.pos.y = self.hitbox.bottom
                self.target = self._choose_target()

        self.hitbox.midbottom = (round(self.pos.x), round(self.pos.y))
        self.pos = pygame.Vector2(self.hitbox.midbottom)
        self.rect.midbottom = self.hitbox.midbottom
