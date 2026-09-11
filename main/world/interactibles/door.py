from world.interactibles.interactible import Interactible
import pygame

class Door(Interactible):
    def __init__(self):
        super().__init__()
        self.state = "closed"  # "closed" oder "open"
        self.sprites = []
        self.closed_images = []
        self.open_images = []
        self.active = True
        self.tilemap = None
        self.collision_rects = []  # Speichert die Collision-Rects, die zu dieser Tür gehören
        self.bounds = None

    def set_sprites(self, sprites, properties=None):
        """Speichert die Sprite-Referenzen, Bilder und Properties."""
        self.sprites = sprites
        self.closed_images = [sprite.image.copy() for sprite in sprites]
        
        # Berechne die Bounds der Sprites
        if sprites:
            rects = [sprite.rect for sprite in sprites]
            self.bounds = rects[0].unionall(rects[1:]) if len(rects) > 1 else rects[0]
        
        # Versuche, die open_images aus properties zu laden
        if properties and "OpenImage" in properties:
            # Falls ein OpenImage Property gesetzt ist, speichere es
            # (würde vom Renderer geladen werden müssen)
            self.open_images = [pygame.Surface((0, 0))] * len(sprites)  # Placeholder
        else:
            # Falls nicht, nutze einfach eine helle Version
            self.open_images = [self._create_open_image(img) for img in self.closed_images]

    def set_tilemap(self, tilemap):
        """Speichert eine Referenz zur tilemap für Kollisionsbearbeitung."""
        self.tilemap = tilemap
        # Finde Collision-Rects, die zu dieser Tür gehören
        if self.bounds and self.tilemap:
            for rect in self.tilemap.collision_rects:
                if self.bounds.colliderect(rect):
                    self.collision_rects.append(rect)

    def _create_open_image(self, original_image):
        """Erstellt ein helleres Bild für die offene Tür."""
        open_img = original_image.copy()
        # Erhöhe die Helligkeit
        open_img.fill((50, 50, 50), special_flags=pygame.BLEND_MULT)
        return open_img

    def on_interact(self):
        print("Door interacted!")
        self.state = "open" if self.state == "closed" else "closed"
        
        # Aktualisiere Sprites
        images = self.open_images if self.state == "open" else self.closed_images
        for i, sprite in enumerate(self.sprites):
            sprite.image = images[i]
        
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