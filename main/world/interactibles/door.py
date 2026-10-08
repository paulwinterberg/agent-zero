from world.interactibles.interactible import Interactible


class Door(Interactible):
    def __init__(self):
        super().__init__()
        self.state = "closed"
        self.locked = False

    def set_tilemap(self, tilemap):
        self.tilemap = tilemap
        if self.bounds:
            door_bounds = [
                rect for rect in tilemap.door_collision_rects
                if self.bounds.colliderect(rect)
            ]
            self.collision_rects = [
                collision
                for collision in tilemap.collision_rects
                if any(collision.colliderect(rect) for rect in door_bounds)
            ]

    def set_sprites(self, sprites, properties=None):
        """Speichert Sprites und erstellt open_images Variante."""
        super().set_sprites(sprites, properties)
        self.locked = self.properties.get(
            "locked", self.properties.get("Locked", False)
        )
        
        # Erstelle die "open" Variante (heller)
        if self.closed_images:
            self.open_images = [self.create_light_version(img) for img in self.closed_images]

    def on_interact(self, held_tool=None):
        """Toggle Tür-State zwischen offen und zu."""
        if self.object_name in ("IronDoor2", "IronDoor3"):
            return False
        if (
            self.state == "closed"
            and self.locked
            and not getattr(held_tool, "can_unlock", False)
        ):
            return False

        if self.state == "closed":
            self.open()
        else:
            self.close()
        return True

    def open(self):
        """Open the door, bypassing key checks for puzzle-controlled doors."""
        if self.state == "open":
            return True

        self.state = "open"
        # Aktualisiere Sprites
        self.update_sprites(self.open_images)
        self._update_collisions()
        return True

    def close(self):
        if self.state == "closed":
            return True

        self.state = "closed"
        self.update_sprites(self.closed_images)
        self._update_collisions()
        return True

    def _update_collisions(self):
        # Aktualisiere Kollisionen
        if self.tilemap:
            if self.state == "open":
                for rect in self.collision_rects:
                    self.tilemap.collision_rects[:] = [
                        collision
                        for collision in self.tilemap.collision_rects
                        if collision is not rect
                    ]
            else:
                for rect in self.collision_rects:
                    if not any(
                        collision is rect
                        for collision in self.tilemap.collision_rects
                    ):
                        self.tilemap.collision_rects.append(rect)