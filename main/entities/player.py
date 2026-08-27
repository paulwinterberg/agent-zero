import pygame
import settings

from world.tilemap import TileMap

class Player(pygame.sprite.Sprite):
    def __init__(self, pos=(0, 0)):
        super().__init__()
        self.image = pygame.Surface((32, 32))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect(center=pos)
        
        # Hitbox setup: full width (32), reduced height (16), aligned to bottom
        hitbox_height = 16
        self.hitbox = pygame.Rect(0, 0, 32, hitbox_height)
        self.hitbox.midbottom = self.rect.midbottom
        
        self.walkspeed = 100
        self.runspeed = 150
        
    def goto(self, pos=(0, 0)):
        self.rect.topleft = pos
        self.hitbox.midbottom = self.rect.midbottom

    def update(self, dt, tilemap: TileMap):
        keys = pygame.key.get_pressed()
        speed = self.walkspeed * dt

        dx = (keys[settings.RIGHT] - keys[settings.LEFT]) * speed
        dy = (keys[settings.BACKWARD] - keys[settings.FORWARD]) * speed

        # Horizontal movement & collisions
        self.hitbox.x += dx
        for r in tilemap.collision_rects:
            if self.hitbox.colliderect(r):
                if dx > 0: self.hitbox.right = r.left
                if dx < 0: self.hitbox.left = r.right

        # Vertical movement & collisions
        self.hitbox.y += dy
        for r in tilemap.collision_rects:
            if self.hitbox.colliderect(r):
                if dy > 0: self.hitbox.bottom = r.top
                if dy < 0: self.hitbox.top = r.bottom

        # Keep sprite image aligned with the hitbox
        self.rect.midbottom = self.hitbox.midbottom