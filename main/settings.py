import pygame

#settings
DISPLAY_CAPTION = "Agent Zero"

TILED_OBJECTS_LAYER_NAME = "Objects"

FORWARD = pygame.K_w
BACKWARD = pygame.K_s
LEFT = pygame.K_a
RIGHT = pygame.K_d
SPRINT = pygame.K_LSHIFT

#paths
SFX_PATH = "assets/sfx"
MUSIC_PATH = "assets/music"
FONTS_PATH = "assets/fonts"
LEVELS_PATH = "assets/levels"
UI_PATH = "assets/ui"

#tilemap settings
TILED_TALL_OBJECT_TILE_THRESHOLD = 2
TILED_OBJECT_OCCLUSION_ALPHA = 100
TILED_OCCLUSION_FADE_SPEED = 600