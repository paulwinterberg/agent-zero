from world.interactibles.door import Door
from world.interactibles.interactible import Interactible


class Button(Interactible):
    """One-use button that opens the door configured in Tiled."""

    def set_sprites(self, sprites, properties=None):
        super().set_sprites(sprites, properties)
        self.pushed = bool(self.properties.get("Pushed", False))
        self.opens_door = self.properties.get("OpensDoor")

    def on_interact(self, held_tool=None):
        if self.pushed:
            return False

        if not self.opens_door:
            raise ValueError(
                f"Button {self.object_name!r} has no OpensDoor property"
            )

        self._open_door(self.opens_door)
        self.pushed = True
        self.properties["Pushed"] = True
        return True

    def _open_door(self, object_name):
        door = self.interaction_manager.get_interactible_instance(object_name)
        if not isinstance(door, Door):
            raise ValueError(f"Interactible door {object_name!r} was not found")
        door.open()
