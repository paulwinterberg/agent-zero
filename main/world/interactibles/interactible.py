import pygame


class Interactible:
    """Basis-Klasse für alle interaktiven Objekte."""
    
    def __init__(self):
        self.sprites = []
        self.state = None  # "closed", "open", etc. - wird in Subklassen definiert
        self.tilemap = None
        self.closed_images = []
        self.open_images = []
        self.bounds = None
        self.collision_rects = []  # Collision-Rects die zu diesem Objekt gehören
    
    def set_sprites(self, sprites, properties=None):
        """Speichert die Sprite-Referenzen und erstellt Kopien der Bilder.
        
        Args:
            sprites: List von pygame Sprite-Objekten
            properties: Dict mit Custom Properties aus Tiled
        """
        self.sprites = sprites
        if sprites:
            self.closed_images = [sprite.image.copy() for sprite in sprites]
            
            # Berechne die Bounds der Sprites
            rects = [sprite.rect for sprite in sprites]
            self.bounds = rects[0].unionall(rects[1:]) if len(rects) > 1 else rects[0]
    
    def set_tilemap(self, tilemap):
        """Speichert eine Referenz zur tilemap und findet zugehörige Collision-Rects.
        
        Args:
            tilemap: Die Tilemap-Instanz
        """
        self.tilemap = tilemap
        if self.bounds and self.tilemap:
            for rect in self.tilemap.collision_rects:
                if self.bounds.colliderect(rect):
                    self.collision_rects.append(rect)
    
    def update_sprites(self, images):
        """Aktualisiert die Bilder aller Sprites dieses Objekts.
        
        Args:
            images: List von pygame Surface-Objekten
        """
        for i, sprite in enumerate(self.sprites):
            if i < len(images):
                sprite.image = images[i]
    
    def create_light_version(self, original_image):
        """Erstellt eine hellere Version eines Bildes (z.B. für offene Tür/Vorhang).
        
        Args:
            original_image: pygame Surface
            
        Returns:
            Hellere Kopie des Bildes
        """
        light_img = original_image.copy()
        light_img.fill((50, 50, 50), special_flags=pygame.BLEND_MULT)
        return light_img
    
    def on_interact(self):
        """Wird aufgerufen wenn der Spieler mit diesem Objekt interagiert.
        Muss in Subklassen überschrieben werden."""
        pass