from core import audio, time, hints
from world.interactibles.interactible import Interactible


class TutorialRadioTower(Interactible):
    
    def __init__(self):
        super().__init__()
        self.can_interact = True
        
        self.send_sound = audio.load_sfx("radio_tower_send.mp3")
        self.send_sound.set_volume(0.2)


    def on_interact(self, tool):
        self.set_enabled(False)
        self.tilemap.show_object_group("RadioTowerSending")
        self.send_sound.play(loops=3)
        time.delay(self.send_sound.get_length() * 4, self._stop_sending_image)
        
    def _stop_sending_image(self):
        self.tilemap.hide_object_group("RadioTowerSending")
        hints.display("You've sent the distress signal! The helicopter is coming. Find a way out to get to it!", should_pause_game=True)