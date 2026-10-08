import settings
import pygame

from typing import TYPE_CHECKING

from entities.entity_state import EntityState
from globals import globs

if TYPE_CHECKING:
    from entities.enemy import Enemy


class IdleState(EntityState):
    def update(self, enemy, dt):
        pass

class PatrolState(EntityState):
    def enter(self, enemy):
        self.path = enemy.path
        self.path_index = 0

    def update(self, enemy, dt):
        if enemy.is_stunned(): return
        
        marker = self.path[self.path_index]
        reached = enemy.move_towards(pygame.math.Vector2(marker.x, marker.y) , dt)
        if reached:
            self.path_index = self.path_index + 1 if self.path_index + 1 < len(self.path) else 0

class ChaseState(EntityState):
    def enter(self, enemy):
        enemy.player_lost_timer = 0
        self.last_known_plr_position = None
        self.path = []
        self.path_index = 0
        self.repath_timer = 0
        self.planned_player_position = None

    def update(self, enemy: "Enemy", dt):
        if enemy.is_stunned():
            return

        player = globs.get("player")
        if player is None:
            return

        if enemy.perception.has_line_of_sight_to_player():
            enemy.player_lost_timer = 0
            self.last_known_plr_position = pygame.Vector2(player.pos)
        else:
            enemy.player_lost_timer += dt

            if enemy.player_lost_timer > settings.ENEMY_PLAYER_LOST_TIMEOUT:
                enemy.change_state(PatrolState() if enemy.path else IdleState())
                return

        if self.last_known_plr_position is None:
            return

        self.repath_timer -= dt
        player_moved = (
            self.planned_player_position is None
            or self.planned_player_position.distance_squared_to(self.last_known_plr_position) >= 16 ** 2
        )
        if self.repath_timer <= 0 or player_moved:
            self.path = enemy.perception.tilemap.find_path(
                enemy.pos,
                self.last_known_plr_position,
                enemy.hitbox.size,
            )
            self.path_index = 0
            self.planned_player_position = self.last_known_plr_position.copy()
            self.repath_timer = 0.35

        if self.path and self.path_index < len(self.path):
            if enemy.move_towards(self.path[self.path_index], dt):
                self.path_index += 1