from world.interactibles.interactible import Interactible


class TutorialRadioTower(Interactible):

    def __init__(self):
        super().__init__()
        self.can_interact = True


    def on_interact(self, tool):
        self.can_interact = False
        self.tilemap.show_object_group("RadioTowerSending")