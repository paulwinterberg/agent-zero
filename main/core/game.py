import core.state_manager as state_manager

from core import renderer, audio
import core.state_manager as state_manager
from states.gameplay import Gameplay
from states.main_menu import MainMenu

def start():
    renderer.init()
    audio.init_audio()
    
    state_manager.push(MainMenu())

    renderer.start_loop(tick)

def tick(dt, events):
    state_manager.update(dt, events)
    state_manager.draw(renderer.screen, dt)