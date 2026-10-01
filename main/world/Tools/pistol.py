import pygame
import math
import settings

from world.Tools.tools import Tools


class Bullet:
    """Kleine schwarze Kugel, die sich durch die Welt bewegt."""

    def __init__(self, position, target, collision_rects, damage):
        self.sprite = pygame.sprite.Sprite()
        self.sprite.image = pygame.Surface((8, 8), pygame.SRCALPHA)
        pygame.draw.circle(self.sprite.image, (0, 0, 0), (4, 4), 4)
        self.sprite.rect = self.sprite.image.get_rect(center=position)
        self.sprite.projectile = self
        self.position = pygame.Vector2(position)
        direction = pygame.Vector2(target) - self.position
        self.velocity = direction.normalize() * 600 if direction.length() else pygame.Vector2()
        self.collision_rects = collision_rects
        self.damage = damage
        self.remaining_time = 2.0

    def update(self, dt, enemies=()):
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
            for enemy in enemies:
                hitbox = getattr(enemy, "hitbox", enemy.rect)
                if hitbox.colliderect(next_rect) and getattr(enemy, "health", 1) > 0:
                    enemy.take_damage(self.damage)
                    return False
            self.position = next_position

        self.sprite.rect.center = round(self.position.x), round(self.position.y)
        self.remaining_time -= dt
        return self.remaining_time > 0


class Pistol(Tools):
    """Mission-Tool, das per Linksklick schwarze Kugeln abfeuert."""

    def __init__(self, position):
        super().__init__()
        self.name = "Pistol"
        self.anzahl = 50
        self.max_anzahl = 50
        self.reload_item_name = "Munition"
        self.consumable = True
        self.keep_when_empty = True
        self.state = "ready"
        self.sprite = pygame.sprite.Sprite()
        self.sprite.image = pygame.Surface((32, 20))
        self.sprite.image.fill((70, 70, 70))
        pygame.draw.rect(self.sprite.image, (0, 0, 0), self.sprite.image.get_rect(), 3)
        self.sprite.rect = self.sprite.image.get_rect(center=position)

        self.damage = settings.PISTOL_DAMAGE

    def fire(self, position, target, tilemap):
        return Bullet(position, target, tilemap.collision_rects, self.damage)