import pygame
import settings
import core.state_manager as state_manager


from globals import globs
from settings import ENEMY_DEFAULT_SPEED #pixels/sec
from enemies.perception import Perception
from enemies.enemy_states import EntityState, IdleState, PatrolState, ChaseState

class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos=(0,0), path: list = None, tool_manager=None):
        super().__init__()

        self.image = pygame.Surface((32, 32), pygame.SRCALPHA)
        self.image.fill((0, 0, 0))
        self.rect = self.image.get_rect(center=pos)

        self.health = settings.ENEMY_DEFAULT_HEALTH
        self.dead = False
        self.stun_time = 0.0
        self.see_player_timer = 0.0

        self.hitbox = pygame.Rect(0, 0, 32, settings.ENEMY_HITBOX_HEIGHT)
        self.hitbox.midbottom = self.rect.midbottom
        self.pos = pygame.math.Vector2(self.hitbox.midbottom)

        self.path = path
        self.tool_manager = tool_manager
        self.tool = None
        self._equip_default_tool()

        self.perception = Perception(self)

        self.state: EntityState = None
        self.change_state(PatrolState() if self.path else IdleState())

    def _equip_default_tool(self):
        if self.tool_manager is None or settings.ENEMY_DEFAULT_TOOL is None:
            return

        if settings.ENEMY_DEFAULT_TOOL != "Pistol":
            raise ValueError(
                f"Unsupported enemy default tool: {settings.ENEMY_DEFAULT_TOOL}"
            )

        from world.Tools.pistol import Pistol

        self.tool = Pistol(self.rect.center)
        self.tool_manager.add_tool(self.tool)
        self.tool.on_interact()
        held_sprite = self.tool.create_held_sprite()
        self.tool_manager.sprite_group.add(
            held_sprite,
            layer=self.tool_manager.tilemap.y_sort_layer(self.rect.bottom),
        )
        
    def fire_tool(self):
        if not self.tool.can_fire: return
        
        projectile = self.tool.fire(
            self.rect.center,
            globs.get("player").rect.center,
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
        if self.tool is not None and self.tool_manager is not None:
            self.tool.drop(self.rect.center)
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
        if self.dead:
            return

        if self.stun_time > 0:
            self.stun_time = max(0, self.stun_time - dt)

        if self.see_player_timer > settings.ENEMY_PLAYER_SPOT_TIME and self.state.__class__ != ChaseState:
            self.change_state(ChaseState())

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
        self._update_held_tool()

    def _update_held_tool(self):
        if (
            self.tool is None
            or self.tool.held_sprite is None
            or self.tool_manager is None
        ):
            return

        player = self.perception.player
        direction = pygame.Vector2(1, 0)
        if player is not None:
            direction = pygame.Vector2(player.rect.center) - self.rect.center
            if direction.length_squared() > 0:
                direction = direction.normalize()
            else:
                direction = pygame.Vector2(1, 0)

        self.tool.held_sprite.rect.center = (
            pygame.Vector2(self.rect.center) + direction * 18
        )
        self.tool_manager.sprite_group.change_layer(
            self.tool.held_sprite,
            self.tool_manager.tilemap.y_sort_layer(self.rect.bottom),
        )