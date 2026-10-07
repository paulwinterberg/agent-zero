from world.interactibles.door import Door


class ContainerDoor(Door):
    """Container doors become invisible while open, but can be closed again."""

    def on_interact(self, held_tool=None):
        if not super().on_interact(held_tool):
            return False

        self._set_visual_state(self.state == "open")
        return True

    def _set_visual_state(self, is_open):
        """Hide the door visually while open, but keep it interactable."""
        alpha = 0 if is_open else 255
        for sprite in self.sprites:
            sprite.image.set_alpha(alpha)
