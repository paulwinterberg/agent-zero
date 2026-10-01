import pygame

from globals import globs
from settings import ENEMY_VISION_RADIUS  # WORLD pixels (not screen pixels)


class Perception:
    def __init__(self, enemy):
        self.enemy = enemy

    @property
    def player(self):
        return globs["player"]

    @property
    def tilemap(self):
        return globs["tilemap"]

    def can_see_player(self) -> bool:
        enemy, player = self.enemy, self.player
        if enemy is None or player is None:
            return False

    
        if not enemy.rect.colliderect(self.tilemap.map_layer.view_rect):
            return False

        start = pygame.Vector2(enemy.rect.center)
        end = pygame.Vector2(player.rect.center)

        # 2. Radius
        if start.distance_squared_to(end) > ENEMY_VISION_RADIUS ** 2:
            return False

        # 3. Line of sight, only testing walls near the ray
        s = (int(start.x), int(start.y))
        e = (int(end.x), int(end.y))
        ray_bounds = pygame.Rect(
            min(s[0], e[0]), min(s[1], e[1]),
            abs(e[0] - s[0]) + 1, abs(e[1] - s[1]) + 1,
        )
        for rect in self.tilemap.collision_rects:
            if rect.colliderect(ray_bounds) and rect.clipline(s, e):
                return False

        return True