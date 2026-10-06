from world.interactibles.door import Door


class ContainerDoor(Door):
    """Container doors disappear after they have been opened."""

    def on_interact(self, held_tool=None):
        if self.state == "open":
            return False

        if not super().on_interact(held_tool):
            return False

        for sprite in self.sprites:
            sprite.kill()

        return True
