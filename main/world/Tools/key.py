import pygame

from world.Tools.tools import Tools


class Key(Tools):
    """Schlüssel zum Öffnen gesperrter Türen."""

    def __init__(self, position):
        super().__init__()
        self.name = "Key"
        self.can_unlock = True
        self.state = "ready"
        self.sprite = pygame.sprite.Sprite()
        self.sprite.image = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.circle(self.sprite.image, (245, 205, 60), (10, 12), 6, 3)
        pygame.draw.line(
            self.sprite.image, (245, 205, 60), (15, 17), (25, 27), 4
        )
        pygame.draw.line(
            self.sprite.image, (245, 205, 60), (22, 24), (22, 29), 3
        )
        pygame.draw.line(
            self.sprite.image, (245, 205, 60), (25, 27), (28, 24), 3
        )
        self.sprite.rect = self.sprite.image.get_rect(center=position)