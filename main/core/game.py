import pygame
import pyscroll
import settings

from entities.player import Player
from world.tilemap import TileMap

screen: pygame.Surface
running = True

tilemap: TileMap
player: Player

group: pyscroll.PyscrollGroup
clock: pygame.time.Clock

def _start_pygame():
    global screen, tilemap, player, group, clock
    pygame.init()
    
    screen = pygame.display.set_mode(settings.DISPLAY_SIZE)
    pygame.display.set_caption(settings.DISPLAY_CAPTION)
    clock = pygame.time.Clock()
    
    tilemap = TileMap("assets\\levels\\tutorial.tmx")
    
    player = Player((tilemap.width / 2, tilemap.height / 2))
    
    group = pyscroll.PyscrollGroup(map_layer=tilemap.map_layer, default_layer=2)
    group.add(player)
    group.add(*tilemap.decorations)
    
def _start_loop():
    global running
    while running:
        dt = clock.tick(60) / 1000
        tick(dt)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

def start():
    _start_pygame()
    _start_loop()
    

def tick(dt):
    player.update(dt, tilemap.collision_rects)
    
    group.change_layer(player, player.rect.bottom)
    group.center(player.rect.center)
    
    group.draw(screen)
    pygame.display.flip()