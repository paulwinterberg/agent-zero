import pygame

from world.Tools.tools import Tools


class Energie(Tools):
    """Pickup, das dem Taser Energie hinzufügt."""

    def __init__(self, position):
        super().__init__()
        self.name = "Energie"
        self.refill_tool_name = "Taser"
        self.refill_amount = 5
        self.state = "ready"
        self.sprite = pygame.sprite.Sprite()
        self.sprite.image = pygame.Surface((28, 28), pygame.SRCALPHA)
        pygame.draw.rect(self.sprite.image, (45, 150, 210), self.sprite.image.get_rect(), 3)
        pygame.draw.polygon(
            self.sprite.image,
            (150, 235, 255),
            [(15, 3), (7, 15), (13, 15), (10, 25), (21, 11), (15, 11)],
        )
        self.sprite.rect = self.sprite.image.get_rect(center=position)