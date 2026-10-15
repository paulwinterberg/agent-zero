import core.state_manager as state_manager
import core.game_data as game_data

from core import renderer, audio
from states.main_menu import MainMenu
from states.intro_video import IntroVideo

def start():
    renderer.init()
    audio.init_audio()
    
    if not game_data.load_game_data()["has_played"]:
        game_data.save_game_data({"has_played": True})
        state_manager.push(IntroVideo())
    else:
        state_manager.push(MainMenu())

    renderer.start_loop(tick)

def tick(dt, events):
    state_manager.update(dt, events)
    state_manager.draw(renderer.screen, dt)