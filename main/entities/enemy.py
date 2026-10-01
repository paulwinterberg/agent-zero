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

        self.health = settings.ENEMY_DEFAULT_HEALTH
        self.stun_time = 0.0
        self.see_player_timer = 0.0

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

    def take_damage(self, dmg: float):
        self.health = max(0, self.health - dmg)

        if self.health == 0:
            self.die()

    def die(self):
        self.image = pygame.Surface((0, 0), pygame.SRCALPHA)

    def stun(self, amount_time: float = 2.0):
        self.stun_time = amount_time

    def is_stunned(self) -> bool:
        return self.stun_time > 0

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
        if self.stun_time > 0:
            self.stun_time = max(0, self.stun_time - dt)

        if self.see_player_timer > settings.ENEMY_PLAYER_SPOT_TIME and self.state.__class__ != ChaseState:
            self.change_state(ChaseState())
            print("Changed state to chase state")

        sees_player = self.perception.can_see_player()
        if sees_player and not self.is_stunned():
            self._draw_exclamation_mark()

            if sees_player:
                self.see_player_timer += dt
            else:
                self.see_player_timer = max(0, self.see_player_timer - dt)
    
        else:
            self.image.fill((0, 0, 0))

        self.state.update(self, dt)