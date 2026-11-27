from core import state_manager, game_data
from states.reception_intro_video import ReceptionIntroVideo
from world.interactibles.interactible import Interactible


class TutorialEscapeHeli(Interactible):
    
    def __init__(self):
        super().__init__()

    def on_interact(self, tool):
        data = game_data.load_game_data()
        data["completed_levels"]["tutorial"] = True
        game_data.save_game_data(data)
        
        state_manager.replace(ReceptionIntroVideo())