import pygame

from world.tools.tools import Tools


class Healing(Tools):
    """Stackbares Verbrauchs-Tool, das den Spieler um 50 Gesundheit heilt."""

    def __init__(self, position):
        super().__init__()
        self.name = "Healing"
        self.anzahl = 1
        self.max_anzahl = 5
        self.stackable = True
        self.secondary_use = True
        self.consumable = True
        self.state = "ready"
        self.sprite = pygame.sprite.Sprite()
        self.sprite.image = pygame.Surface((24, 24), pygame.SRCALPHA)
        pygame.draw.rect(self.sprite.image, (220, 35, 45), (9, 2, 6, 20))
        pygame.draw.rect(self.sprite.image, (220, 35, 45), (2, 9, 20, 6))
        self.sprite.rect = self.sprite.image.get_rect(center=position)

    def secondary_action(self, player):
        if player.health >= player.max_health:
            return False

        player.health = min(player.max_health, player.health + 100)
        return True
