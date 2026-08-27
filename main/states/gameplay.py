import pygame

from entities.player import Player
from states.state import State
from core.renderer import load_tilemap, render_world


class Gameplay(State):
    def __init__(self):
        self.player = Player()
        self.tilemap, self.group = load_tilemap("assets/levels/hq_lobby.tmx", self.player)
        
        self.tilemap.zoom_to(4)
        
        spawnPoint = self.tilemap.get_object("Spawns", "PlayerSpawn")
        self.player.goto((spawnPoint.x, spawnPoint.y))
    
    def update(self, dt, events):
        self.player.update(dt, self.tilemap)
    
    def draw(self, screen, dt):
        render_world(dt, self.tilemap, self.group, self.player)