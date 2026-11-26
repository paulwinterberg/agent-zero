from core import audio
from world.interactibles.interactible import Interactible


class TutorialRadioTower(Interactible):

    def __init__(self):
        super().__init__()
        self.can_interact = True
        
        self.send_sound = audio.load_sfx("radio_tower_send.mp3")
        self.send_sound.set_volume(0.2)


    def on_interact(self, tool):
        self.can_interact = False
        self.tilemap.show_object_group("RadioTowerSending")
        self.send_sound.play(loops=3)