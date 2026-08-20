import pygame

from entities.player import Player
from core import renderer
from core.state_manager import StateManager
from states.gameplay import Gameplay
from world.tilemap import TileMap
from states.main_menu import MainMenu

state_manager = StateManager()

def start():
    renderer.init()
    
    state_manager.push(MainMenu())
    
    renderer.start_loop(tick)
    

def tick(dt, events):
    state_manager.update(dt, events)
    state_manager.draw(renderer.screen, dt)