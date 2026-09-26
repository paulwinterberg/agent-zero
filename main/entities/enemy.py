import pygame
import settings
import core.state_manager as state_manager

from settings import ENEMY_DEFAULT_SPEED #pixels/sec
from enemies.perception import Perception
from enemies.enemy_states import EntityState, IdleState, PatrolState, ChaseState

class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos=(0,0), path: list = None):
        super().__init__()

        self.image = pygame.Surface((32, 32), pygame.SRCALPHA)
        self.image.fill((0, 0, 0))
        self.rect = self.image.get_rect(center=pos)

        self.hitbox = pygame.Rect(0, 0, 32, settings.ENEMY_HITBOX_HEIGHT)
        self.hitbox.midbottom = self.rect.midbottom
        self.pos = pygame.math.Vector2(self.hitbox.midbottom)

        self.path = path

        self.perception = Perception(self)

        self.state: EntityState = None
        self.change_state(PatrolState() if self.path else IdleState())

    def change_state(self, new_state):
        if self.state:
            self.state.exit(self)
        self.state = new_state
        self.state.enter(self)

    def goto(self, pos: pygame.math.Vector2 | tuple[float, float]):
        self.pos = pygame.math.Vector2(pos)

    def move_towards(self, target: pygame.math.Vector2 | tuple[float, float], dt) -> bool:
        target = pygame.math.Vector2(target)
        offset = target - self.pos
        distance = offset.length()

        reached = False

        if distance <= ENEMY_DEFAULT_SPEED * dt:
            self.pos = target
            reached = True
        elif distance > 0:
            self.pos += offset.normalize() * ENEMY_DEFAULT_SPEED * dt

        self.hitbox.midbottom = (round(self.pos.x), round(self.pos.y))
        self.rect.midbottom = self.hitbox.midbottom

        return reached
    
    def _draw_exclamation_mark(self):
        marker = pygame.Surface((10, 50), pygame.SRCALPHA)
        pygame.draw.line(marker, (255, 0, 0), (5, 2), (5, 12), 3)
        pygame.draw.circle(marker, (255, 0, 0), (5, 15), 2)
        self.image.blit(marker, (11, 0))

    def update(self, dt):
        if self.perception.can_see_player():
            self._draw_exclamation_mark()
        else:
            self.image.fill((0, 0, 0))

        self.state.update(self, dt)