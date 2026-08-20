import pygame

class Player(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((32, 32))
        self.image.fill((255, 0, 0))  # placeholder art
        self.rect = self.image.get_rect(center=pos)

    def update(self, dt, collision_rects):
        keys = pygame.key.get_pressed()
        speed = 200 * dt

        dx = (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * speed
        dy = (keys[pygame.K_DOWN] - keys[pygame.K_UP]) * speed

        self.rect.x += dx
        for r in collision_rects:
            if self.rect.colliderect(r):
                if dx > 0: self.rect.right = r.left
                if dx < 0: self.rect.left = r.right

        self.rect.y += dy
        for r in collision_rects:
            if self.rect.colliderect(r):
                if dy > 0: self.rect.bottom = r.top
                if dy < 0: self.rect.top = r.bottom