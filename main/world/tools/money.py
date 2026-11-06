import pygame

from world.tools.tools import Tools


class Money(Tools):
    """Collectible cash pickup worth 100 credits."""

    def __init__(self, position):
        super().__init__()
        self.name = "Money"
        self.value = 100
        self.state = "ready"
        self.sprite = pygame.sprite.Sprite()
        self.sprite.image = pygame.Surface((18, 18), pygame.SRCALPHA)
        pygame.draw.circle(self.sprite.image, (238, 199, 76), (9, 9), 8)
        pygame.draw.circle(self.sprite.image, (255, 232, 149), (9, 9), 5)
        pygame.draw.line(self.sprite.image, (178, 138, 26), (9, 2), (9, 16), 2)
        pygame.draw.line(self.sprite.image, (178, 138, 26), (2, 9), (16, 9), 2)
        self.sprite.rect = self.sprite.image.get_rect(center=position)
