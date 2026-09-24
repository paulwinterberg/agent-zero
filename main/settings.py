import pygame

#settings
DISPLAY_CAPTION = "Agent Zero"

#tiled
TILED_OBJECTS_LAYER_NAME = "Objects"
TILED_SPAWNS_LAYER_NAME = "Spawns"

#keybinds
FORWARD = pygame.K_w
BACKWARD = pygame.K_s
LEFT = pygame.K_a
RIGHT = pygame.K_d
SPRINT = pygame.K_LSHIFT
SLIDE = pygame.K_c
INTERACT = pygame.K_f

#enemies
ENEMY_PLAYER_SPOT_TIME = 3.0
ENEMY_PLAYER_LOST_TIMEOUT = 5.0
ENEMY_VISION_RADIUS = 100 #pixels
ENEMY_DEFAULT_SPEED = 25 #pixels/sec

#hitboxes
PLAYER_HITBOX_HEIGHT = 8
ENEMY_HITBOX_HEIGHT = 8

#sliding & sprinting
SLIDETIME = .5
SLIDECOOLDOWN = 3
SPRINT_STAMINA_PERCENT_THRESHOLD = 0.3

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