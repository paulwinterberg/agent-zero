import pygame
import pyscroll
import settings
import pygame_gui

from entities.player.player import Player
from world.tilemap import TileMap
import core.screen as screen_module

screen: pygame.Surface
ui_manager: pygame_gui.UIManager
running = True

clock: pygame.time.Clock

def init():
    global screen, clock, ui_manager
    pygame.init()

    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.display.set_caption(settings.DISPLAY_CAPTION)

    clock = pygame.time.Clock()

    screen_size = screen_module.get_screen_size()
    print(screen_size)
    ui_manager = pygame_gui.UIManager((screen_size.x, screen_size.y))

def start_loop(tickFunc):
    global running
    while running:
        dt = clock.tick(60) / 1000.0

        events = pygame.event.get()

        tickFunc(dt, events)
        for event in events:
            if event.type == pygame.QUIT:
                running = False

            ui_manager.process_events(event)
        ui_manager.update(dt)


def render_world(dt, tilemap: TileMap, group: pyscroll.PyscrollGroup, player: Player):
    tilemap.update_occlusion(player, dt)
    group.change_layer(player, tilemap.y_sort_layer(player.rect.bottom))
    group.center(player.rect.center)
    group.draw(screen)

def render_ui():
    ui_manager.draw_ui(screen)


def load_tilemap(path, player: Player) -> tuple[TileMap, pyscroll.PyscrollGroup]:
    tilemap = TileMap(path)

    group = pyscroll.PyscrollGroup(
        map_layer=tilemap.map_layer,
        default_layer=tilemap.sort_base_layer
    )
    group.add(player, layer=tilemap.y_sort_layer(player.rect.bottom))
    group.add(*tilemap.objects)

    return tilemap, group

def get_ui_manager():
    return ui_manager