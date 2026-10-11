from core import renderer, audio
from core.state_manager import StateManager
from states.main_menu import MainMenu

state_manager = StateManager()

def start():
    renderer.init()
    audio.init_audio()
    
    state_manager.push(MainMenu())

    renderer.start_loop(tick)

def tick(dt, events):
    state_manager.update(dt, events)
    state_manager.draw(renderer.screen, dt)