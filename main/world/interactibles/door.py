import math

import pygame

from world.interactibles.interactible import Interactible


class Door(Interactible):
    PUZZLE_DOOR_NAMES = ("IronDoor2", "IronDoor3", "IronDoor4")

    def __init__(self):
        super().__init__()
        self.state = "closed"
        self.locked = False
        self.lock_visible = False
        self.locked_images = []

    def set_tilemap(self, tilemap):
        self.tilemap = tilemap
        self.collision_rects = []
        if self.bounds and self.tilemap:
            self.collision_rects = [
                rect for rect in self.tilemap.collision_rects
                if self.bounds.colliderect(rect)
            ]
            if self.sprites:
                bottom = max(sprite.rect.bottom for sprite in self.sprites)
                bottom_rects = [
                    sprite.rect for sprite in self.sprites
                    if sprite.rect.bottom == bottom
                ]
                bottom_collision = bottom_rects[0].unionall(bottom_rects[1:])
                if bottom_collision not in self.collision_rects:
                    self.collision_rects.append(bottom_collision)
            self._sync_collision_state()

    def _sync_collision_state(self):
        if not self.tilemap or not self.collision_rects:
            return

        if self.state == "open":
            self.tilemap.collision_rects = [
                rect for rect in self.tilemap.collision_rects
                if rect not in self.collision_rects
            ]
        else:
            for rect in self.collision_rects:
                if rect not in self.tilemap.collision_rects:
                    self.tilemap.collision_rects.append(rect)

    def set_sprites(self, sprites, properties=None):
        """Speichert Sprites und erstellt open_images Variante."""
        super().set_sprites(sprites, properties)
        self.locked = self.properties.get(
            "locked", self.properties.get("Locked", False)
        )
        
        if self.closed_images:
            self.open_images = [self.create_light_version(img) for img in self.closed_images]
            if self.object_name in self.PUZZLE_DOOR_NAMES:
                self.lock_visible = True
                self.locked_images = [image.copy() for image in self.closed_images]
                self._draw_lock(self.locked_images[-1])
                self.update_sprites(self.locked_images)

    def _draw_lock(self, image):
        """Draw a prominent padlock over the lower tile of a puzzle door."""
        black = (35, 27, 18)
        gold = (245, 190, 62)
        pygame.draw.arc(image, black, (8, 0, 16, 21), math.pi, math.tau, 5)
        pygame.draw.arc(image, gold, (10, 2, 12, 17), math.pi, math.tau, 3)
        pygame.draw.rect(image, black, (4, 11, 24, 19), border_radius=4)
        pygame.draw.rect(image, gold, (6, 13, 20, 15), border_radius=3)
        pygame.draw.circle(image, black, (16, 19), 2)
        pygame.draw.rect(image, black, (15, 20, 2, 5), border_radius=1)

    def on_interact(self, held_tool=None):
        """Toggle Tür-State zwischen offen und zu."""
        if self.object_name in self.PUZZLE_DOOR_NAMES:
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
        self.lock_visible = False
        self._sync_collision_state()
        # Aktualisiere Sprites
        self.update_sprites(self.open_images)
        return True

    def close(self):
        if self.state == "closed":
            return True

        self.state = "closed"
        self._sync_collision_state()
        self.update_sprites(
            self.locked_images if self.lock_visible else self.closed_images
        )
        return True