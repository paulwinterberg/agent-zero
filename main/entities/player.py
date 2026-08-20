import pygame
import settings

from world.tilemap import TileMap

class Player(pygame.sprite.Sprite):
    def __init__(self, pos=(0, 0)):
        super().__init__()
        self.image = pygame.Surface((32, 32))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect(center=pos)
        
        self.walkspeed = 100
        self.runspeed = 150
        
    def goto(self, pos=(0,0)):
        self.rect.x, self.rect.y = pos

    def update(self, dt, tilemap: TileMap):
        keys = pygame.key.get_pressed()
        speed = self.walkspeed * dt

        dx = (keys[settings.RIGHT] - keys[settings.LEFT]) * speed
        dy = (keys[settings.BACKWARD] - keys[settings.FORWARD]) * speed

        self.rect.x += dx
        for r in tilemap.collision_rects:
            if self.rect.colliderect(r):
                if dx > 0: self.rect.right = r.left
                if dx < 0: self.rect.left = r.right

        self.rect.y += dy
        for r in tilemap.collision_rects:
            if self.rect.colliderect(r):
                if dy > 0: self.rect.bottom = r.top
                if dy < 0: self.rect.top = r.bottom