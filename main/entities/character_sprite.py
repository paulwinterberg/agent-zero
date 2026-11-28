from pathlib import Path

import pygame


def load_character_frame(filename, frame_size, display_size, frame_origin=(0, 0)):
    sprite_sheet_path = (
        Path(__file__).resolve().parents[2] / "assets" / "enemys" / filename
    )
    sprite_sheet = pygame.image.load(str(sprite_sheet_path))
    frame = sprite_sheet.subsurface(pygame.Rect(frame_origin, frame_size)).copy()
    bounds = frame.get_bounding_rect()
    if bounds.width and bounds.height:
        frame = frame.subsurface(bounds).copy()

    scale = min(
        display_size[0] / frame.get_width(),
        display_size[1] / frame.get_height(),
    )
    scaled_size = (
        max(1, round(frame.get_width() * scale)),
        max(1, round(frame.get_height() * scale)),
    )
    return pygame.transform.scale(frame, scaled_size)
