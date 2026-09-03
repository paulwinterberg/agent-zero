from core import renderer, audio
from core.state_manager import StateManager
from states.gameplay import Gameplay
from states.main_menu import MainMenu

state_manager = StateManager()

def start():
    renderer.init()
    audio.init_audio()
    
    state_manager.push(Gameplay())

    try:
        renderer.start_loop(tick)
    except:
        exit()

def tick(dt, events):
    state_manager.update(dt, events)
    state_manager.draw(renderer.screen, dt)