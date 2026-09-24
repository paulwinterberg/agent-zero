import pygame

from world.Tools.tools import Tools


class Munition(Tools):
    """Pickup, das der Pistole Munition hinzufügt."""

    def __init__(self, position):
        super().__init__()
        self.name = "Munition"
        self.refill_tool_name = "Pistol"
        self.refill_amount = 50
        self.state = "ready"
        self.sprite = pygame.sprite.Sprite()
        self.sprite.image = pygame.Surface((30, 22))
        self.sprite.image.fill((210, 175, 45))
        pygame.draw.rect(self.sprite.image, (70, 45, 20), self.sprite.image.get_rect(), 3)
        pygame.draw.line(self.sprite.image, (255, 235, 130), (7, 7), (23, 7), 3)
        pygame.draw.line(self.sprite.image, (255, 235, 130), (7, 15), (23, 15), 3)
        self.sprite.rect = self.sprite.image.get_rect(center=position)