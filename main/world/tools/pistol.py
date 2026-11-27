import math
import settings
import pygame

from entities.player.player import Player
from world.tools.tools import Tools, load_tool_texture
from core import audio


class Bullet:

    def __init__(
        self,
        position,
        target,
        collision_rects,
        damage,
        is_enemy=False,
        speed=settings.PISTOL_BULLET_SPEED,
        target_enemies_only=False,
    ):
        self.sprite = pygame.sprite.Sprite()
        texture = load_tool_texture("bullet", size=(8, 8))
        if texture is not None:
            base_image = texture
        else:
            base_image = pygame.Surface((8, 8), pygame.SRCALPHA)
            pygame.draw.circle(base_image, (0, 0, 0), (4, 4), 4)
        self.sprite.projectile = self
        self.position = pygame.Vector2(position)

        direction = pygame.Vector2(target) - self.position
        self.velocity = (
            direction.normalize() * speed
            if direction.length()
            else pygame.Vector2()
        )
        if self.velocity.length_squared():
            angle = 180 - math.degrees(math.atan2(self.velocity.y, self.velocity.x))
            self.sprite.image = pygame.transform.rotate(base_image, angle)
        else:
            self.sprite.image = base_image
        self.sprite.rect = self.sprite.image.get_rect(center=position)
        self.collision_rects = collision_rects
        self.damage = damage
        self.remaining_time = 2.0
        self.is_enemy = is_enemy
        self.target_enemies_only = target_enemies_only

    @staticmethod
    def _swept_hit(start, end, target_start, target_end, target_size, bullet_size):
        relative_start = start - target_start
        relative_end = end - target_end
        relative_movement = relative_end - relative_start
        half_size = (pygame.Vector2(target_size) + pygame.Vector2(bullet_size)) / 2

        entry_time = 0.0
        exit_time = 1.0
        for axis in ("x", "y"):
            start_offset = getattr(relative_start, axis)
            movement = getattr(relative_movement, axis)
            extent = getattr(half_size, axis)
            if movement == 0:
                if abs(start_offset) > extent:
                    return False
                continue

            first = (-extent - start_offset) / movement
            second = (extent - start_offset) / movement
            entry_time = max(entry_time, min(first, second))
            exit_time = min(exit_time, max(first, second))
            if entry_time > exit_time:
                return False

        return exit_time >= 0 and entry_time <= 1

    def update(self, dt, enemies=()):
        movement = self.velocity * dt
        enemy_sweeps = []
        max_enemy_movement = 0
        for enemy in enemies:
            hitbox = getattr(enemy, "hitbox", enemy.rect)
            previous_hitbox = getattr(enemy, "previous_hitbox", hitbox)
            previous_center = pygame.Vector2(previous_hitbox.center)
            enemy_movement = pygame.Vector2(hitbox.center) - previous_center
            max_enemy_movement = max(max_enemy_movement, enemy_movement.length())
            enemy_sweeps.append((enemy, previous_hitbox, enemy_movement))

        steps = max(1, math.ceil((movement.length() + max_enemy_movement) / 4))
        step = movement / steps
        for step_index in range(1, steps + 1):
            previous_fraction = (step_index - 1) / steps
            fraction = step_index / steps
            previous_position = self.position
            next_position = self.position + step
            next_rect = self.sprite.image.get_rect(
                center=(round(next_position.x), round(next_position.y))
            )

            for enemy, previous_hitbox, enemy_movement in enemy_sweeps:
                if self.is_enemy and not (
                    isinstance(enemy, Player) or getattr(enemy, "allied", False)
                ):
                    continue
                if self.target_enemies_only and (
                    isinstance(enemy, Player) or getattr(enemy, "allied", False)
                ):
                    continue
                if getattr(enemy, "health", 1) <= 0:
                    continue

                target_start = pygame.Vector2(previous_hitbox.center) + (
                    enemy_movement * previous_fraction
                )
                target_end = pygame.Vector2(previous_hitbox.center) + (
                    enemy_movement * fraction
                )
                if self._swept_hit(
                    previous_position,
                    next_position,
                    target_start,
                    target_end,
                    previous_hitbox.size,
                    self.sprite.image.get_size(),
                ):
                    enemy.take_damage(self.damage)
                    return False

            if any(next_rect.colliderect(rect) for rect in self.collision_rects):
                return False
            self.position = next_position

        self.sprite.rect.center = round(self.position.x), round(self.position.y)
        self.remaining_time -= dt
        return self.remaining_time > 0


class Pistol(Tools):
    """Mission-Tool, das per Linksklick schwarze Kugeln abfeuert."""

    def __init__(
        self,
        position,
        name="Pistol",
        max_ammo=None,
        shot_cooldown=None,
        projectile_speed=None,
    ):
        super().__init__()
        self.name = name
        self.max_amount = (
            settings.PISTOL_MAX_AMMO if max_ammo is None else max_ammo
        )
        self.amount = self.max_amount
        self.reload_item_name = "Ammo"
        self.consumable = True
        self.can_fire = True
        self.keep_when_empty = True
        self.aim_held_sprite = True
        self.shot_cooldown = (
            settings.PISTOL_COOLDOWN
            if shot_cooldown is None
            else shot_cooldown
        )
        self.projectile_speed = (
            settings.PISTOL_BULLET_SPEED
            if projectile_speed is None
            else projectile_speed
        )
        self.state = "ready"
        self.sprite = pygame.sprite.Sprite()
        texture = load_tool_texture("pistol", size=(32, 20))
        if texture is not None:
            self.sprite.image = texture
        else:
            self.sprite.image = pygame.Surface((32, 20))
            self.sprite.image.fill((70, 70, 70))
            pygame.draw.rect(self.sprite.image, (0, 0, 0), self.sprite.image.get_rect(), 3)
        self.sprite.rect = self.sprite.image.get_rect(center=position)

        self.damage = settings.PISTOL_DAMAGE
        
        self.sound = audio.load_sfx("pistol_shot.mp3")

    def fire(self, position, target, tilemap, target_enemies_only=False):
        self.sound.play()
        return Bullet(
            position,
            target,
            tilemap.collision_rects,
            self.damage,
            is_enemy=self.is_enemy,
            speed=self.projectile_speed,
            target_enemies_only=target_enemies_only,
        )