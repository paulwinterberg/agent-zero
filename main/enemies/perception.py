import pygame

from globals import globs
from settings import ENEMY_VISION_RADIUS #pixels
from core import screen

class Perception:
    def __init__(self, enemy):
        self.enemy = enemy
        self.player = globs["player"]
        self.tilemap = globs["tilemap"]

    def can_see_player(self) -> bool:
        if self.enemy is None or self.player is None:
            return False

        enemy_pos = self.enemy.pos
        player_pos = self.player.pos

        if enemy_pos is None or player_pos is None:
            return False

        screen_size = screen.get_screen_size()
        camera_center = self.player.rect.center if getattr(self.player, "rect", None) is not None else player_pos
        visible_rect = pygame.Rect(
            camera_center[0] - screen_size.x // 2,
            camera_center[1] - screen_size.y // 2,
            screen_size.x,
            screen_size.y,
        )

        enemy_rect = getattr(self.enemy, "rect", None)
        if enemy_rect is not None:
            if not enemy_rect.colliderect(visible_rect):
                return False
        elif not visible_rect.collidepoint(enemy_pos.x, enemy_pos.y):
            return False

        if enemy_pos.distance_to(player_pos) > ENEMY_VISION_RADIUS:
            return False

        collision_rects = self.tilemap.collision_rects

        start = (int(enemy_pos.x), int(enemy_pos.y))
        end = (int(player_pos.x), int(player_pos.y))

        for rect in collision_rects:
            if rect.clipline(start, end):
                return False

        return True