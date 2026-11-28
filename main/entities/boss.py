import pygame
import settings

from entities.character_sprite import load_character_frame
from entities.enemy import Enemy
from globals import globs
from settings import ENEMY_VISION_RADIUS


class BossEnemy(Enemy):
    PHASES = (
        (200.0, settings.PISTOL_COOLDOWN * 2),
        (250.0, settings.PISTOL_COOLDOWN * 1.5),
        (200.0, settings.PISTOL_COOLDOWN),
    )
    MINION_SPAWN_INTERVAL = 30.0

    def __init__(self, pos, tool_manager=None, spawn_minions=None):
        super().__init__(pos, tool_manager=tool_manager)
        self.image = load_character_frame("AgentX.png", (48, 72), (48, 56))
        self.base_image = self.image.copy()
        self.rect = self.image.get_rect(midbottom=self.hitbox.midbottom)
        self.phase = 1
        self.allied = False
        self.enemy_manager = None
        self.spawn_minions = spawn_minions
        self.phase_spawn_elapsed = 0.0
        self.ally_shot_cooldown = 0.0
        self.follow_repath_timer = 0.0
        self.follow_path = []
        self.follow_path_index = 0
        self.follow_goal = None
        if self.tool is not None:
            self.tool.projectile_speed = settings.PISTOL_BULLET_SPEED / 2
        self._set_phase(1)

    def _set_phase(self, phase):
        self.phase = phase
        self.max_health, self.fire_cooldown = self.PHASES[phase - 1]
        self.health = self.max_health
        if self.tool is not None:
            self.tool.shot_cooldown = self.fire_cooldown

    def take_damage(self, dmg):
        if self.dead or self.allied or not self.perception.can_see_player():
            return

        self.health = max(0, self.health - dmg)
        if self.health > 0:
            return

        if self.phase < len(self.PHASES):
            self._set_phase(self.phase + 1)
            self.phase_spawn_elapsed = 0.0
            if self.spawn_minions is not None:
                self.spawn_minions(self)
        else:
            self._become_ally()

    def _become_ally(self):
        self.allied = True
        self.phase = len(self.PHASES) + 1
        self.health = self.max_health
        self.see_player_timer = 0
        self.image = self.base_image.copy()
        self.fire_cooldown = settings.PISTOL_COOLDOWN
        if self.tool is not None:
            self.tool.is_enemy = False
            self.tool.shot_cooldown = settings.PISTOL_COOLDOWN
            self.tool.projectile_speed = settings.PISTOL_BULLET_SPEED
        if self.tool_manager is not None:
            for sprite in self.tool_manager.sprite_group.sprites():
                projectile = getattr(sprite, "projectile", None)
                if getattr(projectile, "owner", None) is self:
                    sprite.kill()

    def update(self, dt):
        if self.allied:
            self._update_ally(dt)
            return

        super().update(dt)
        if self.dead or self.phase != 3:
            return

        self.phase_spawn_elapsed += dt
        while self.phase_spawn_elapsed >= self.MINION_SPAWN_INTERVAL:
            self.phase_spawn_elapsed -= self.MINION_SPAWN_INTERVAL
            if self.spawn_minions is not None:
                self.spawn_minions(self)

    def _update_ally(self, dt):
        player = globs.get("player")
        if player is None:
            return

        self.ally_shot_cooldown = max(0, self.ally_shot_cooldown - dt)
        target = self._find_enemy_target()
        if target is not None:
            distance_to_player = pygame.Vector2(self.rect.center).distance_to(
                player.rect.center
            )
            if distance_to_player <= ENEMY_VISION_RADIUS:
                self._move_ally_towards(target.hitbox.midbottom, dt, 96)
                if (
                    self.tool is not None
                    and self.tool_manager is not None
                    and self.ally_shot_cooldown <= 0
                    and self.perception.has_line_of_sight(target)
                ):
                    projectile = self.tool.fire(
                        self.rect.center,
                        target.rect.center,
                        self.perception.tilemap,
                        target_enemies_only=True,
                    )
                    self.tool_manager.add_projectile(projectile, self)
                    self.ally_shot_cooldown = settings.PISTOL_COOLDOWN
                return

        self._move_ally_towards(player.hitbox.midbottom, dt, 72)

    def _find_enemy_target(self):
        if self.enemy_manager is None:
            return None

        candidates = []
        for enemy in self.enemy_manager.enemies:
            if enemy is self or enemy.dead or getattr(enemy, "allied", False):
                continue
            distance = pygame.Vector2(self.rect.center).distance_to(
                self.perception.center_of(enemy)
            )
            if (
                distance <= ENEMY_VISION_RADIUS
                and self.perception.has_line_of_sight(enemy)
            ):
                candidates.append((distance, enemy))

        return min(candidates, key=lambda candidate: candidate[0])[1] if candidates else None

    def _move_ally_towards(self, goal, dt, stop_distance):
        goal = pygame.Vector2(goal)
        if self.pos.distance_squared_to(goal) <= stop_distance ** 2:
            self.follow_path = []
            self.follow_goal = goal
            return

        self.follow_repath_timer -= dt
        goal_changed = (
            self.follow_goal is None
            or self.follow_goal.distance_squared_to(goal) >= 32 ** 2
        )
        if self.follow_repath_timer <= 0 or goal_changed:
            self.follow_path = self.perception.tilemap.find_path(
                self.pos, goal, self.hitbox.size
            )
            self.follow_path_index = 0
            self.follow_goal = goal.copy()
            self.follow_repath_timer = 0.35

        if self.follow_path and self.follow_path_index < len(self.follow_path):
            if self.move_towards(self.follow_path[self.follow_path_index], dt):
                self.follow_path_index += 1
        else:
            self.move_towards(goal, dt)
