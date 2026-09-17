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
        hitbox_height = 8
        self.hitbox = pygame.Rect(0, 0, 32, hitbox_height)
        self.hitbox.midbottom = self.rect.midbottom

        # Float position tracker for the hitbox's midbottom point.
        # pygame.Rect only stores ints, so we keep the "real" position here
        # and round into the Rect each frame -- otherwise any movement
        # smaller than 1px per frame (very common) gets silently truncated
        # to 0, which is why movement could randomly seem to "not happen".
        self.pos = pygame.math.Vector2(self.hitbox.midbottom)

        self.walkspeed = 50
        self.runspeed = 60
        self.fastrunspeed = 100
        self.slidespeed = 250
        self.slidetime = 0
        self.slidecooldown = 0

        self.stamina_max = 5
        self.stamina = self.stamina_max

    def goto(self, pos=(0, 0)):
        self.rect.topleft = pos
        self.hitbox.midbottom = self.rect.midbottom
        self.pos = pygame.math.Vector2(self.hitbox.midbottom)

    def update(self, dt, tilemap: TileMap):
        self.slidetime = max(0, self.slidetime - dt)
        self.slidecooldown = max(0, self.slidecooldown - dt)

        keys = pygame.key.get_pressed()
        speed = self.walkspeed

        if keys[settings.SPRINT] and keys[settings.SLIDE] and self.slidecooldown == 0:
            self.slidetime = settings.SLIDETIME
            self.slidecooldown = settings.SLIDECOOLDOWN

        # Stamina regenerates passively every frame...
        self.stamina = min(self.stamina_max, self.stamina + dt)

        if self.slidetime > 0:
            speed = self.slidespeed
        elif keys[settings.SPRINT] and self.stamina > 0:
            speed = self.runspeed
            self.runspeed = min(self.fastrunspeed, self.runspeed + dt * 100)
            # ...and is spent (net) while actively sprinting.
            self.stamina = max(0, self.stamina - dt * 2)
        else:
            speed = self.walkspeed
            self.runspeed = max(self.walkspeed, self.runspeed - dt * 80)
        speed *= dt

        dx = (keys[settings.RIGHT] - keys[settings.LEFT]) * speed
        dy = (keys[settings.BACKWARD] - keys[settings.FORWARD]) * speed

        # --- Horizontal movement & collisions (float-based) ---
        self.pos.x += dx
        self.hitbox.x = round(self.pos.x - self.hitbox.width / 2)
        for r in tilemap.collision_rects:
            if self.hitbox.colliderect(r):
                if dx > 0:
                    self.hitbox.right = r.left
                if dx < 0:
                    self.hitbox.left = r.right
                self.pos.x = self.hitbox.x + self.hitbox.width / 2

        # --- Vertical movement & collisions (float-based) ---
        self.pos.y += dy
        self.hitbox.y = round(self.pos.y - self.hitbox.height)
        for r in tilemap.collision_rects:
            if self.hitbox.colliderect(r):
                if dy > 0:
                    self.hitbox.bottom = r.top
                if dy < 0:
                    self.hitbox.top = r.bottom
                self.pos.y = self.hitbox.bottom

        # Keep pos, hitbox and rect all in sync (midbottom of hitbox)
        self.hitbox.midbottom = (round(self.pos.x), round(self.pos.y))
        self.pos = pygame.math.Vector2(self.hitbox.midbottom)
        self.rect.midbottom = self.hitbox.midbottom