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
        self.upper_collision = None

    def set_tilemap(self, tilemap):
        self.tilemap = tilemap
        self.collision_rects = []
        if self.bounds and self.tilemap:
            if self.sprites:
                bottom = max(sprite.rect.bottom for sprite in self.sprites)
                bottom_rects = [
                    sprite.rect for sprite in self.sprites
                    if sprite.rect.bottom == bottom
                ]
                bottom_collision = bottom_rects[0].unionall(bottom_rects[1:])
                self.collision_rects = [bottom_collision]
                upper_collision = pygame.Rect(
                    self.bounds.left,
                    self.bounds.top,
                    self.bounds.width,
                    bottom_collision.top - self.bounds.top,
                )
                self.tilemap.collision_rects = [
                    piece
                    for rect in self.tilemap.collision_rects
                    for piece in self._subtract_rect(rect, self.bounds)
                ]
                self.upper_collision = upper_collision
            self._sync_collision_state()

    @staticmethod
    def _subtract_rect(rect, cutout):
        overlap = rect.clip(cutout)
        if overlap.width <= 0 or overlap.height <= 0:
            return [rect]

        return [
            piece
            for piece in (
                pygame.Rect(rect.left, rect.top, rect.width, overlap.top - rect.top),
                pygame.Rect(rect.left, overlap.bottom, rect.width, rect.bottom - overlap.bottom),
                pygame.Rect(rect.left, overlap.top, overlap.left - rect.left, overlap.height),
                pygame.Rect(overlap.right, overlap.top, rect.right - overlap.right, overlap.height),
            )
            if piece.width > 0 and piece.height > 0
        ]

    def _sync_collision_state(self):
        if not self.tilemap or not self.collision_rects:
            return

        if self.state == "open":
            self.tilemap.collision_rects = [
                rect for rect in self.tilemap.collision_rects
                if all(rect is not door_rect for door_rect in self.collision_rects)
            ]
        else:
            for rect in self.collision_rects:
                if all(rect is not existing for existing in self.tilemap.collision_rects):
                    self.tilemap.collision_rects.append(rect)

    def _sync_container_collision_state(self):
        if not self.tilemap or not self.collision_rects:
            return

        if self.state == "open":
            self.tilemap.collision_rects = [
                rect for rect in self.tilemap.collision_rects
                if rect not in self.collision_rects
                and not (
                    self.upper_collision
                    and rect.colliderect(self.upper_collision)
                )
            ]
            self.tilemap.collision_rects = [
                rect for rect in self.tilemap.collision_rects
                if not rect.colliderect(self.bounds)
            ]
        else:
            if self.upper_collision:
                self.tilemap.collision_rects = [
                    rect for rect in self.tilemap.collision_rects
                    if rect not in (self.upper_collision,)
                    and not rect.colliderect(self.upper_collision)
                ]
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