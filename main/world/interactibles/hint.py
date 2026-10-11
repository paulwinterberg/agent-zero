from world.interactibles.interactible import Interactible


class Hint(Interactible):
    """A readable hint that pauses gameplay while it is open."""

    def __init__(self):
        super().__init__()
        self.opened = False

    def on_interact(self, held_tool=None):
        self.opened = True
        return True

    def close(self):
        self.opened = False
