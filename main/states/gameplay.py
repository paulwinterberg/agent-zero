import pygame
import pygame_gui
import settings
import pygame_gui

from entities.player.player import Player
from states.state import State
from core.renderer import load_tilemap, render_world, get_ui_manager, get_ui_manager
from core.interactions import InteractionManager
from world.Tools.red_block import MissionToolManager, RedBlock

class Gameplay(State):
    def __init__(self):
        self.player = Player()
        self.tilemap, self.group = load_tilemap("assets/levels/testlevel.tmx", self.player)
        self.interaction_manager = InteractionManager()
        self.tool_manager = MissionToolManager()
        
        self.tilemap.zoom_to(4)
        
        spawnPoint = self.tilemap.get_object("Spawns", "PlayerSpawn")
        self.player.goto((spawnPoint.x, spawnPoint.y))

        red_block_position = (self.player.rect.centerx + 40, self.player.rect.centery)
        red_block = RedBlock(red_block_position)
        self.tool_manager.add_tool(
            red_block,
            self.group,
            self.tilemap.y_sort_layer(red_block.sprite.rect.bottom)
        )

        self.stamina_bar = pygame_gui.elements.UIProgressBar(
            relative_rect=pygame.Rect((20, 20), (200, 25)),
            manager=get_ui_manager()
        )
    
    def update(self, dt, events):
        self.player.update(dt, self.tilemap)
        self.interaction_manager.update(dt, self.player, self.tilemap)
        self.tool_manager.update(dt, self.player)
        
        # Prüfe auf F-Taste Druck für Interaktion
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == settings.INTERACT:
                    self.interaction_manager.try_interact()
                    self.tool_manager.try_interact()
    
    def draw(self, screen, dt):
        render_world(dt, self.tilemap, self.group, self.player)

        