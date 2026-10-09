import pygame

import settings
from world.Tools.tools import Tools, load_tool_texture

class Cocaine(Tools):
    """Stackbares Kokain-Pickup mit kurzem Geschwindigkeitsschub."""

    def __init__(self, position):
        super().__init__()
        self.name = "Kokain"
        self.anzahl = 1
        self.max_anzahl = 5
        self.stackable = True
        self.secondary_use = True
        self.consumable = True
        self.keep_when_empty = True
        self.state = "ready"
        self.sprite = pygame.sprite.Sprite()
        texture = load_tool_texture("cocaine", size=(24, 20))
        if texture is not None:
            self.sprite.image = texture
        else:
            self.sprite.image = pygame.Surface((24, 20), pygame.SRCALPHA)
            pygame.draw.polygon(
                self.sprite.image,
                (238, 235, 220),
                ((3, 6), (8, 2), (20, 4), (22, 14), (16, 18), (4, 15)),
            )
            pygame.draw.polygon(
                self.sprite.image,
                (120, 45, 45),
                ((3, 6), (8, 2), (20, 4), (22, 14), (16, 18), (4, 15)),
                2,
            )
            pygame.draw.line(self.sprite.image, (120, 45, 45), (7, 7), (18, 12), 2)
        self.sprite.rect = self.sprite.image.get_rect(center=position)

    def secondary_action(self, player):
        if self.anzahl <= 0:
            return False

        player.activate_cocaine_speed_boost(settings.COCAINE_SPEED_BOOST_DURATION)
        return True
