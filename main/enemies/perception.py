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
        return self.can_see_target(self.player)

    def targets(self):
        targets = []
        player = self.player
        if player is not None:
            targets.append(player)

        ally = globs.get("agent_x")
        if ally is not None and ally.allied and not ally.dead:
            targets.append(ally)
        return targets

    def visible_targets(self):
        return [target for target in self.targets() if self.can_see_target(target)]

    def center_of(self, target):
        if target is self.player:
            return pygame.Vector2(target.rect.center)
        return pygame.Vector2(getattr(target, "hitbox", target.rect).center)

    def can_see_target(self, target) -> bool:
        enemy = self.enemy
        if enemy is None or target is None:
            return False

        if not enemy.hitbox.colliderect(self.tilemap.map_layer.view_rect):
            return False

        start = self.center_of(enemy)
        end = self.center_of(target)
        if start.distance_squared_to(end) > ENEMY_VISION_RADIUS ** 2:
            return False

        return self.has_line_of_sight(target)

    def has_line_of_sight_to_player(self) -> bool:
        return self.has_line_of_sight(self.player)

    def has_line_of_sight(self, target) -> bool:
        enemy = self.enemy
        if enemy is None or target is None:
            return False

        start = self.center_of(enemy)
        end = self.center_of(target)

        s = (int(start.x), int(start.y))
        e = (int(end.x), int(end.y))
        ray_bounds = pygame.Rect(
            min(s[0], e[0]), min(s[1], e[1]),
            abs(e[0] - s[0]) + 1, abs(e[1] - s[1]) + 1,
        )
        for rect in self.tilemap.collision_rects:
            if rect.colliderect(ray_bounds) and rect.clipline(s, e):
                return False

        from world.tools.smoke_bomb import active_smoke_clouds

        for cloud in list(active_smoke_clouds):
            rect = cloud.sprite.rect
            if rect.colliderect(ray_bounds) and rect.clipline(s, e):
                return False
    
        return True