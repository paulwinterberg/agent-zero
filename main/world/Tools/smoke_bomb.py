import math

import pygame

from world.Tools.tools import Tools


class SmokeCloud:
    """Kurzlebiger, wachsender Rauchbereich."""

    def __init__(self, position):
        self.sprite = pygame.sprite.Sprite()
        self.sprite.image = pygame.Surface((144, 144), pygame.SRCALPHA)
        smoke = self.sprite.image
        pygame.draw.circle(smoke, (38, 38, 38, 225), (72, 74), 50)
        pygame.draw.circle(smoke, (58, 58, 58, 215), (42, 62), 42)
        pygame.draw.circle(smoke, (48, 48, 48, 220), (103, 58), 45)
        pygame.draw.circle(smoke, (75, 75, 75, 205), (31, 91), 35)
        pygame.draw.circle(smoke, (65, 65, 65, 215), (75, 40), 39)
        pygame.draw.circle(smoke, (52, 52, 52, 220), (105, 99), 42)
        pygame.draw.circle(smoke, (88, 88, 88, 190), (63, 108), 35)
        pygame.draw.circle(smoke, (35, 35, 35, 220), (121, 83), 29)
        self.sprite.rect = self.sprite.image.get_rect(center=position)
        self.sprite.projectile = self
        self.base_image = self.sprite.image.copy()
        self.elapsed = 0.0
        self.duration = 4.5

    def update(self, dt):
        self.elapsed += dt
        progress = min(self.elapsed / self.duration, 1.0)
        scale = 0.9 + progress * 0.6
        size = round(144 * scale)
        self.sprite.image = pygame.transform.scale(self.base_image, (size, size))
        self.sprite.image.set_alpha(round(230 * (1.0 - progress)))
        self.sprite.rect = self.sprite.image.get_rect(center=self.sprite.rect.center)
        return self.elapsed < self.duration


class SmokeBombProjectile:
    """Kurz geworfene Rauchbombe, die am Ende eine Rauchwolke erzeugt."""

    def __init__(self, position, target, collision_rects):
        self.sprite = pygame.sprite.Sprite()
        self.sprite.image = pygame.Surface((12, 12), pygame.SRCALPHA)
        pygame.draw.circle(self.sprite.image, (35, 35, 35), (6, 6), 6)
        pygame.draw.circle(self.sprite.image, (180, 180, 180), (4, 4), 2)
        self.sprite.rect = self.sprite.image.get_rect(center=position)
        self.sprite.projectile = self
        self.position = pygame.Vector2(position)
        direction = pygame.Vector2(target) - self.position
        self.velocity = direction.normalize() * 180 if direction.length() else pygame.Vector2()
        self.collision_rects = collision_rects
        self.remaining_time = 0.45

    def update(self, dt):
        movement = self.velocity * dt
        steps = max(1, math.ceil(movement.length() / 4))
        step = movement / steps
        for _ in range(steps):
            next_position = self.position + step
            next_rect = self.sprite.image.get_rect(
                center=(round(next_position.x), round(next_position.y))
            )
            if any(next_rect.colliderect(rect) for rect in self.collision_rects):
                return False
            self.position = next_position

        self.sprite.rect.center = round(self.position.x), round(self.position.y)
        self.remaining_time -= dt
        return self.remaining_time > 0

    def on_expire(self):
        return SmokeCloud(self.position)


class SmokeBomb(Tools):
    """Verbrauchbares Tool, das per Rechtsklick eine Rauchwolke erzeugt."""

    def __init__(self, position):
        super().__init__()
        self.name = "Smoke Bomb"
        self.secondary_use = True
        self.consumable = True
        self.state = "ready"
        self.sprite = pygame.sprite.Sprite()
        self.sprite.image = pygame.Surface((24, 24), pygame.SRCALPHA)
        pygame.draw.circle(self.sprite.image, (35, 35, 35), (12, 12), 9)
        pygame.draw.circle(self.sprite.image, (170, 170, 170), (9, 9), 3)
        self.sprite.rect = self.sprite.image.get_rect(center=position)

    def fire(self, position, target, tilemap):
        return SmokeBombProjectile(position, target, tilemap.collision_rects)