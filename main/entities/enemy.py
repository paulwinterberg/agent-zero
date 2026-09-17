import pygame
import settings

from enemies.perception import Perception
from enemies.enemy_states import EntityState, IdleState, PatrolState, ChaseState

class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos=(0,0)):
        super().__init__()

        self.image = pygame.Surface((32, 32))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect(center=pos)

        self.hitbox = pygame.Rect(0, 0, 32, settings.ENEMY_HITBOX_HEIGHT)
        self.hitbox.midbottom = self.rect.midbottom
        self.pos = pygame.math.Vector2(self.hitbox.midbottom)

        self.perception = Perception(self)

        self.state: EntityState = IdleState()

    def change_state(self, new_state):
        self.state.exit(self)
        self.state = new_state
        self.state.enter(self)

    def update(self, dt):
        self.state.update(self, dt)