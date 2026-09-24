from world.interactibles.interactible import Interactible


class Door(Interactible):
    def __init__(self):
        super().__init__()
        self.state = "closed"
        self.locked = False

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
        if self.locked and not getattr(held_tool, "can_unlock", False):
            return False

        self.state = "open" if self.state == "closed" else "closed"
        
        # Aktualisiere Sprites
        images = self.open_images if self.state == "open" else self.closed_images
        self.update_sprites(images)
        
        # Aktualisiere Kollisionen
        if self.tilemap:
            if self.state == "open":
                # Entferne Collision-Rects
                for rect in self.collision_rects:
                    if rect in self.tilemap.collision_rects:
                        self.tilemap.collision_rects.remove(rect)
            else:
                # Füge Collision-Rects wieder hinzu
                for rect in self.collision_rects:
                    if rect not in self.tilemap.collision_rects:
                        self.tilemap.collision_rects.append(rect)

        return True