import pygame

from world.Tools.tools import Tools


class RedBlock(Tools):
    """Ein einfacher roter Test-Block zum Aufheben."""

    def __init__(self, position):
        super().__init__()
        self.name = "Red Block"
        self.state = "ready"
        self.sprite = pygame.sprite.Sprite()
        self.sprite.image = pygame.Surface((32, 32))
        self.sprite.image.fill((255, 40, 40))
        pygame.draw.rect(self.sprite.image, (255, 255, 255), self.sprite.image.get_rect(), 3)
        self.sprite.rect = self.sprite.image.get_rect(center=position)

