from world.interactibles.door import Door
from world.interactibles.interactible import Interactible


class Button(Interactible):
    """One-use button that opens its configured door when its button group is pushed."""

    BUTTON_GROUPS = {
        "IronDoor2": ("Button1_319",),
        "IronDoor3": ("Button1_318", "Button1_305"),
        "IronDoor4": ("Button1_478", "Button1_328"),
    }

    def set_sprites(self, sprites, properties=None):
        super().set_sprites(sprites, properties)
        self.pushed = bool(self.properties.get("Pushed", False))
        self.opens_door = self.properties.get("OpensDoor") or next(
            (
                door_name
                for door_name, button_names in self.BUTTON_GROUPS.items()
                if self.object_name in button_names
            ),
            None,
        )

    def on_interact(self, held_tool=None):
        if self.pushed:
            return False

        if not self.opens_door:
            return False

        self.pushed = True
        self.properties["Pushed"] = True
        if self.interaction_manager.are_buttons_for_door_pushed(self.opens_door):
            self._open_door(self.opens_door)
        return True

    def _open_door(self, object_name):
        door = self.interaction_manager.get_interactible_instance(object_name)
        if not isinstance(door, Door):
            raise ValueError(f"Interactible door {object_name!r} was not found")
        door.open()
