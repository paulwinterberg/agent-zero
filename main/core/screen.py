import pygame

def get_screen_size() -> pygame.Vector2:
    surface = pygame.display.get_surface()
    return pygame.Vector2(surface.get_size()) if surface else pygame.Vector2(0, 0)

def get_screen_center() -> pygame.Vector2:
    return get_screen_size()/2

def set_caption(caption: str):
    pygame.display.set_caption(caption)