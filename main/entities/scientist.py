import pygame

from entities.character_sprite import load_character_frame


class Scientist(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = load_character_frame("Siencentist.png", (32, 32), (32, 32))
        self.rect = self.image.get_rect(midbottom=pos)
