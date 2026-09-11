from world.interactibles.interactible import Interactible


class Curtains(Interactible):
    """Interaktive Vorhänge - können offen/zu sein."""
    
    def __init__(self):
        super().__init__()
        self.state = "closed"  # "closed" oder "open"

    def set_sprites(self, sprites, properties=None):
        """Speichert Sprites und erstellt open_images Variante."""
        super().set_sprites(sprites, properties)
        
        # Erstelle die "open" Variante (heller)
        if self.closed_images:
            self.open_images = [self.create_light_version(img) for img in self.closed_images]

    def on_interact(self):
        """Toggle Vorhang-State zwischen offen und zu."""
        self.state = "open" if self.state == "closed" else "closed"
        
        # Aktualisiere Sprites
        images = self.open_images if self.state == "open" else self.closed_images
        self.update_sprites(images)
        
        # Optional: Vorhänge können auch Licht durchlassen
        # Hier könnte man z.B. die Helligkeit des Levels anpassen
