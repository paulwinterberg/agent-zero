import pygame
import pygame_gui
import settings
import pygame_gui

from entities.player import Player
from states.state import State
from core.renderer import load_tilemap, render_world, get_ui_manager, get_ui_manager
from core.interactions import InteractionManager

class Gameplay(State):
    def __init__(self):
        self.player = Player()
        self.tilemap, self.group = load_tilemap("assets/levels/hq_lobby.tmx", self.player)
        self.interaction_manager = InteractionManager()
        
        self.tilemap.zoom_to(4)
        
        spawnPoint = self.tilemap.get_object("Spawns", "PlayerSpawn")
        self.player.goto((spawnPoint.x, spawnPoint.y))

        self.stamina_bar = pygame_gui.elements.UIProgressBar(
            relative_rect=pygame.Rect((20, 20), (200, 25)),
            manager=get_ui_manager()
        )
    
    def update(self, dt, events):
        self.player.update(dt, self.tilemap)
        self.interaction_manager.update(dt, self.player, self.tilemap)
        
        # Prüfe auf F-Taste Druck für Interaktion
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == settings.INTERACT:
                    self.interaction_manager.try_interact()
    
    def draw(self, screen, dt):
        render_world(dt, self.tilemap, self.group, self.player)

        

        