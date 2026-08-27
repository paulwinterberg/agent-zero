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
    group.center(player.rect.center)
    group.draw(screen)
    
def load_tilemap(path, player: Player) -> tuple[TileMap, pyscroll.PyscrollGroup]:
    tilemap = TileMap(path)

    player_layer = tilemap.get_layer_index("Player") or 2

    group = pyscroll.PyscrollGroup(map_layer=tilemap.map_layer, default_layer=player_layer)
    group.add(player)
    group.add(*tilemap.decorations)

    return tilemap, group