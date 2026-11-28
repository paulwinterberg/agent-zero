import pygame
import settings
import core.state_manager as state_manager


from globals import globs
from settings import ENEMY_DEFAULT_SPEED #pixels/sec
from entities.character_sprite import load_character_frame
from enemies.perception import Perception
from enemies.enemy_states import EntityState, IdleState, PatrolState, ChaseState
from world.tools.registry import tool_name_to_class_map

class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos=(0,0), path: list = None, tool_manager=None, groupId=""):
        super().__init__()

        spawn_rect = pygame.Rect(0, 0, 32, 32)
        spawn_rect.center = pos
        self.hitbox = pygame.Rect(0, 0, 32, settings.ENEMY_HITBOX_HEIGHT)
        self.hitbox.midbottom = spawn_rect.midbottom
        self.previous_hitbox = self.hitbox.copy()
        self.pos = pygame.math.Vector2(self.hitbox.midbottom)

        self.image = load_character_frame(
            "enemys.png",
            (48, 80),
            (48, 64),
            frame_origin=(104, 0),
        )
        self.base_image = self.image.copy()
        self.rect = self.image.get_rect(midbottom=self.hitbox.midbottom)

        self.health = settings.ENEMY_DEFAULT_HEALTH
        self.max_health = self.health
        self.fire_cooldown = settings.ENEMY_DEFAULT_FIRE_COOLDOWN
        self.dead = False
        self.stun_time = 0.0
        self.see_player_timer = 0.0

        self.groupId = groupId
        self.group = [self]

        self.path = path
        self.tool_manager = tool_manager
        self.tool = None
        self._equip_default_tool()

        self.perception = Perception(self)

        self.state: EntityState = None
        self.change_state(PatrolState() if self.path else IdleState())
        
    def set_group(self, group):
        self.group = group

    def _equip_default_tool(self):
        if self.tool_manager is None or settings.ENEMY_DEFAULT_TOOL is None:
            return

        self.tool = tool_name_to_class_map.get(settings.ENEMY_DEFAULT_TOOL)(
            self.hitbox.center
        )
        self.tool.is_enemy = True
        self.tool_manager.add_tool(self.tool)
        self.tool.on_interact()
        held_sprite = self.tool.create_held_sprite()
        self.tool_manager.sprite_group.add(
            held_sprite,
            layer=self.tool_manager.tilemap.y_sort_layer(self.hitbox.bottom),
        )
        
    def fire_tool(self, target=None):
        if self.tool is None or not self.tool.can_fire:
            return

        target = target or globs.get("player")
        if target is None:
            return
        
        projectile = self.tool.fire(
            self.perception.center_of(self),
            self.perception.center_of(target),
            globs.get("tilemap"),
        )
        self.tool_manager.add_projectile(projectile, self)

    def change_state(self, new_state):
        if self.state:
            self.state.exit(self)
        self.state = new_state
        self.state.enter(self)

    def take_damage(self, dmg: float):
        if self.dead:
            return

        self.health = max(0, self.health - dmg)

        if self.health == 0:
            self.die()

    def die(self):
        if self.dead:
            return

        self.dead = True
        self.image = pygame.Surface((0, 0), pygame.SRCALPHA)
        if self.tool_manager is not None:
            self.tool_manager.money += 50
        if self.tool is not None and self.tool_manager is not None:
            self.tool.drop(self.perception.center_of(self))
            self.tool_manager.add_tool(self.tool)

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
        motion = offset.normalize() * min(distance, ENEMY_DEFAULT_SPEED * dt) if distance > 0 else pygame.Vector2()
        tilemap = self.perception.tilemap

        self.pos.x += motion.x
        self.hitbox.x = round(self.pos.x - self.hitbox.width / 2)
        for rect in tilemap.collision_rects:
            if self.hitbox.colliderect(rect):
                if motion.x > 0:
                    self.hitbox.right = rect.left
                elif motion.x < 0:
                    self.hitbox.left = rect.right
                self.pos.x = self.hitbox.x + self.hitbox.width / 2

        self.pos.y += motion.y
        self.hitbox.y = round(self.pos.y - self.hitbox.height)
        for rect in tilemap.collision_rects:
            if self.hitbox.colliderect(rect):
                if motion.y > 0:
                    self.hitbox.bottom = rect.top
                elif motion.y < 0:
                    self.hitbox.top = rect.bottom
                self.pos.y = self.hitbox.bottom

        self.hitbox.midbottom = (round(self.pos.x), round(self.pos.y))
        self.pos = pygame.math.Vector2(self.hitbox.midbottom)
        self.rect.midbottom = self.hitbox.midbottom

        return self.pos.distance_squared_to(target) <= 1
    
    def _draw_exclamation_mark(self):
        marker = pygame.Surface((10, 50), pygame.SRCALPHA)
        pygame.draw.line(marker, (255, 0, 0), (5, 2), (5, 12), 3)
        pygame.draw.circle(marker, (255, 0, 0), (5, 15), 2)
        self.image.blit(marker, (11, 0))

    def update(self, dt):
        self.previous_hitbox = self.hitbox.copy()
        if self.dead:
            return

        if self.stun_time > 0:
            self.stun_time = max(0, self.stun_time - dt)

        self.image = self.base_image.copy()
        visible_targets = self.perception.visible_targets()
        if (
            visible_targets
            and self.see_player_timer > settings.ENEMY_PLAYER_SPOT_TIME
            and self.state.__class__ != ChaseState
        ):
            for enemy in self.group:
                enemy.change_state(ChaseState())

        if visible_targets and not self.is_stunned():
            self._draw_exclamation_mark()
            self.see_player_timer += dt
        else:
            self.see_player_timer = max(0, self.see_player_timer - dt)

        self.state.update(self, dt)
        self._update_held_tool()

    def _update_held_tool(self):
        if (
            self.tool is None
            or self.tool.held_sprite is None
            or self.tool_manager is None
        ):
            return

        target = getattr(self.state, "target", None)
        if target is None:
            target = self.perception.player
        direction = pygame.Vector2(1, 0)
        if target is not None:
            direction = (
                self.perception.center_of(target)
                - self.perception.center_of(self)
            )
            if direction.length_squared() > 0:
                direction = direction.normalize()
            else:
                direction = pygame.Vector2(1, 0)

        self.tool.held_sprite.rect.center = (
            self.perception.center_of(self) + direction * 18
        )
        self.tool_manager.sprite_group.change_layer(
            self.tool.held_sprite,
            self.tool_manager.tilemap.y_sort_layer(self.hitbox.bottom),
        )