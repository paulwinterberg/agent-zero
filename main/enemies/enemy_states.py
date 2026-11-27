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
        self.last_fire_time = -10000
        self.accumulated = 0
        self.target = None
        self.last_known_target_position = None
        self.path = []
        self.path_index = 0
        self.repath_timer = 0
        self.planned_target_position = None

    def update(self, enemy: "Enemy", dt):
        self.accumulated += dt
        
        if enemy.is_stunned():
            return

        targets = enemy.perception.visible_targets()
        if targets:
            target = min(
                targets,
                key=lambda candidate: pygame.Vector2(enemy.rect.center).distance_squared_to(
                    candidate.rect.center
                ),
            )
            enemy.player_lost_timer = 0
            self.target = target
            self.last_known_target_position = pygame.Vector2(target.pos)

            if (
                enemy.tool is not None
                and self.accumulated - self.last_fire_time > enemy.fire_cooldown
                and enemy.tool.can_fire
            ):
                enemy.fire_tool(target)
                self.last_fire_time = self.accumulated
        else:
            enemy.player_lost_timer += dt

            if enemy.player_lost_timer > settings.ENEMY_PLAYER_LOST_TIMEOUT:
                enemy.change_state(PatrolState() if enemy.path else IdleState())
                return

        if self.last_known_target_position is None:
            return

        self.repath_timer -= dt
        target_moved = (
            self.planned_target_position is None
            or self.planned_target_position.distance_squared_to(
                self.last_known_target_position
            ) >= 16 ** 2
        )
        if self.repath_timer <= 0 or target_moved:
            self.path = enemy.perception.tilemap.find_path(
                enemy.pos,
                self.last_known_target_position,
                enemy.hitbox.size,
            )
            self.path_index = 0
            self.planned_target_position = self.last_known_target_position.copy()
            self.repath_timer = 0.35

        if self.path and self.path_index < len(self.path):
            if enemy.move_towards(self.path[self.path_index], dt):
                self.path_index += 1