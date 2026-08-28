import pygame
import pyscroll
import settings

from entities.player import Player
from world.tilemap import TileMap

screen: pygame.Surface
running = True

clock: pygame.time.Clock

def init():
    global screen, clock
    pygame.init()
    
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.display.set_caption(settings.DISPLAY_CAPTION)
    clock = pygame.time.Clock()
    
def start_loop(tickFunc):
    global running
    while running:
        try:
            dt = clock.tick(60) / 1000
        except:
            exit()
        
        events = pygame.event.get()
        
        tickFunc(dt, events)
        for event in events:
            if event.type == pygame.QUIT:
                running = False
    
def render_world(dt, tilemap: TileMap, group: pyscroll.PyscrollGroup, player: Player):
    group.change_layer(player, tilemap.y_sort_layer(player.rect.bottom))
    group.center(player.rect.center)
    group.draw(screen)

    
def load_tilemap(path, player: Player) -> tuple[TileMap, pyscroll.PyscrollGroup]:
    tilemap = TileMap(path)

    group = pyscroll.PyscrollGroup(
        map_layer=tilemap.map_layer,
        default_layer=tilemap.sort_base_layer
    )
    group.add(player, layer=tilemap.y_sort_layer(player.rect.bottom))
    group.add(*tilemap.decorations)
    group.add(*tilemap.walls)

    return tilemap, group