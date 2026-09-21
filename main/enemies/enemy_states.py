import settings

from typing import TYPE_CHECKING

from entities.entity_state import EntityState

if TYPE_CHECKING:
    from entities.enemy import Enemy


class IdleState(EntityState):
    def update(self, enemy, dt):
        pass

class PatrolState(EntityState):
    def update(self, enemy, dt):
        #entity.move_along_current_path(dt)
        pass

class ChaseState(EntityState):
    def enter(self, enemy):
        enemy.alert_timer = 0
        enemy.player_lost_timer = 0
        pass

    def update(self, enemy: "Enemy", dt):
        if enemy.alert_timer < settings.ENEMY_PLAYER_SPOT_TIME:
            return

        if not enemy.can_see_player():
            enemy.player_lost_timer += dt

            if enemy.player_lost_timer > settings.ENEMY_PLAYER_LOST_TIMEOUT:
                enemy.change_state(PatrolState())
            return

        enemy.face_player()
        enemy.try_shoot()