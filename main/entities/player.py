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
        
        self.walkspeed = 50
        self.runspeed = 60
        self.fastrunspeed = 100
        self.slidespeed = 250
        self.slidetime = 0
        self.slidecooldown = 0
        self.steminacooldown = 0
        
    def goto(self, pos=(0, 0)):
        self.rect.topleft = pos
        self.hitbox.midbottom = self.rect.midbottom

    def update(self, dt, tilemap: TileMap):
        self.slidetime = max(0, self.slidetime - dt)
        self.slidecooldown = max(0, self.slidecooldown - dt)
        self.steminacooldown = max(0, self.steminacooldown - dt)
        keys = pygame.key.get_pressed()
        speed = self.walkspeed
        if keys[settings.SPRINT] and keys[settings.SLIDE] and self.slidecooldown == 0:
            self.slidetime = settings.SLIDETIME
            self.slidecooldown = settings.SLIDECOOLDOWN
        if self.slidetime > 0:
            speed = self.slidespeed
        elif keys[settings.SPRINT] and self.steminacooldown < 5:
            speed = self.runspeed
            self.runspeed = min(self.fastrunspeed, self.runspeed + dt * 100)
            self.steminacooldown += dt*2
        else:
            speed = self.walkspeed
            self.runspeed = max(self.walkspeed, self.runspeed - dt * 80)
        speed *= dt
        
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