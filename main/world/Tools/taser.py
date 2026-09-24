import pygame

from world.Tools.tools import Tools


class TaserSpark:
    """Kurz sichtbarer blauer Blitz in Richtung des Mauszeigers."""

    def __init__(self, position, target):
        self.sprite = pygame.sprite.Sprite()
        self.sprite.image = pygame.Surface((180, 180), pygame.SRCALPHA)
        self.sprite.rect = self.sprite.image.get_rect(center=position)
        self.sprite.projectile = self
        self.remaining_time = 0.18

        direction = pygame.Vector2(target) - pygame.Vector2(position)
        if direction.length_squared() == 0:
            direction = pygame.Vector2(1, 0)
        direction = direction.normalize()
        perpendicular = pygame.Vector2(-direction.y, direction.x)
        origin = pygame.Vector2(90, 90)

        for index, offset in enumerate((-8, 0, 8)):
            points = [origin + perpendicular * offset]
            for step in range(1, 5):
                distance = step * 18
                jitter = perpendicular * (6 if (step + index) % 2 else -6)
                points.append(origin + direction * distance + jitter)
            pygame.draw.lines(self.sprite.image, (70, 180, 255), False, points, 2)

    def update(self, dt):
        self.remaining_time -= dt
        return self.remaining_time > 0


class Taser(Tools):
    """Mission-Tool, das beim Linksklick kurze blaue Blitze sprüht."""

    def __init__(self, position):
        super().__init__()
        self.name = "Taser"
        self.anzahl = 20
        self.max_anzahl = 20
        self.reload_item_name = "Energie"
        self.consumable = True
        self.keep_when_empty = True
        self.state = "ready"
        self.sprite = pygame.sprite.Sprite()
        self.sprite.image = pygame.Surface((32, 24))
        self.sprite.image.fill((210, 30, 30))
        pygame.draw.rect(self.sprite.image, (255, 220, 220), self.sprite.image.get_rect(), 2)
        self.sprite.rect = self.sprite.image.get_rect(center=position)

    def fire(self, position, target, tilemap):
        return TaserSpark(position, target)