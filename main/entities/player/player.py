import pygame
import settings

from world.tilemap import TileMap

from settings import SPRINT_STAMINA_PERCENT_THRESHOLD


class Player(pygame.sprite.Sprite):
    def __init__(self, pos=(0, 0)):
        super().__init__()
        self.image = pygame.Surface((32, 32))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect(center=pos)

        hitbox_height = 8
        self.hitbox = pygame.Rect(0, 0, 32, hitbox_height)
        self.hitbox.midbottom = self.rect.midbottom
        self.pos = pygame.math.Vector2(self.hitbox.midbottom)

        # --- movement speeds ---
        self.walkspeed = 50
        self.runspeed_base = 60
        self.runspeed_max = 100
        self.runspeed = self.runspeed_base   # current sprint speed, ramps up over time
        self.runspeed_accel = 100            # units/sec^2 while sprinting
        self.runspeed_decel = 80             # units/sec^2 while not sprinting

        self.slidespeed = 250
        self.slidetime = 0.0
        self.slidecooldown = 0.0
        self.slide_dir = pygame.math.Vector2()

        # --- stamina ---
        self.stamina_max = 5.0
        self.stamina = self.stamina_max
        self.stamina_drain_rate = 1.0   # per second while sprinting
        self.stamina_regen_rate = .5   # per second while not sprinting
        self.is_sprinting = False

        # last facing direction, used so sliding has something to lock onto
        self.facing = pygame.math.Vector2(0, 1)

    def get_stamina_percent(self):
        return self.stamina / self.stamina_max

    def goto(self, pos=(0, 0)):
        self.rect.topleft = pos
        self.hitbox.midbottom = self.rect.midbottom
        self.pos = pygame.math.Vector2(self.hitbox.midbottom)

    def _get_input_dir(self, keys):
        dx = keys[settings.RIGHT] - keys[settings.LEFT]
        dy = keys[settings.BACKWARD] - keys[settings.FORWARD]
        direction = pygame.math.Vector2(dx, dy)
        if direction.length_squared() > 0:
            direction = direction.normalize()
        return direction

    def _update_timers(self, dt):
        self.slidetime = max(0.0, self.slidetime - dt)
        self.slidecooldown = max(0.0, self.slidecooldown - dt)

    def _try_start_slide(self, keys, move_dir):
        can_slide = (
            keys[settings.SPRINT]
            and keys[settings.SLIDE]
            and self.slidecooldown == 0
            and self.slidetime == 0
        )
        if can_slide:
            self.slidetime = settings.SLIDETIME
            self.slidecooldown = settings.SLIDECOOLDOWN
            # lock the slide to current facing so releasing/changing keys mid-slide
            # doesn't let you steer it like normal movement
            self.slide_dir = move_dir if move_dir.length_squared() > 0 else self.facing

    def _resolve_speed_and_stamina(self, keys, dt):
        """Returns the speed (units/sec) to move at this frame."""
        if self.slidetime > 0:
            self.stamina = min(self.stamina_max, self.stamina + self.stamina_regen_rate * dt)
            self.is_sprinting = False
            return self.slidespeed

        wants_sprint = keys[settings.SPRINT]

        if self.is_sprinting:
            # Already sprinting: keep going until stamina actually hits 0.
            can_continue = self.stamina > 0
        else:
            # Not sprinting yet: need to clear the threshold to start.
            can_continue = self.get_stamina_percent() > settings.SPRINT_STAMINA_PERCENT_THRESHOLD

        self.is_sprinting = wants_sprint and can_continue

        if self.is_sprinting:
            self.stamina = max(0.0, self.stamina - self.stamina_drain_rate * dt)
            self.runspeed = min(self.runspeed_max, self.runspeed + self.runspeed_accel * dt)
            return self.runspeed
        else:
            self.stamina = min(self.stamina_max, self.stamina + self.stamina_regen_rate * dt)
            self.runspeed = max(self.runspeed_base, self.runspeed - self.runspeed_decel * dt)
            return self.walkspeed

    def _move_and_collide(self, motion, tilemap: TileMap):
        # horizontal
        self.pos.x += motion.x
        self.hitbox.x = round(self.pos.x - self.hitbox.width / 2)
        for r in tilemap.collision_rects:
            if self.hitbox.colliderect(r):
                if motion.x > 0:
                    self.hitbox.right = r.left
                elif motion.x < 0:
                    self.hitbox.left = r.right
                self.pos.x = self.hitbox.x + self.hitbox.width / 2

        # vertical
        self.pos.y += motion.y
        self.hitbox.y = round(self.pos.y - self.hitbox.height)
        for r in tilemap.collision_rects:
            if self.hitbox.colliderect(r):
                if motion.y > 0:
                    self.hitbox.bottom = r.top
                elif motion.y < 0:
                    self.hitbox.top = r.bottom
                self.pos.y = self.hitbox.bottom

    def update(self, dt, tilemap: TileMap):
        self._update_timers(dt)

        keys = pygame.key.get_pressed()
        move_dir = self._get_input_dir(keys)
        if move_dir.length_squared() > 0:
            self.facing = move_dir

        self._try_start_slide(keys, move_dir)
        speed = self._resolve_speed_and_stamina(keys, dt)

        direction = self.slide_dir if self.slidetime > 0 else move_dir
        motion = direction * speed * dt

        self._move_and_collide(motion, tilemap)

        # Keep pos, hitbox and rect all in sync (midbottom of hitbox)
        self.hitbox.midbottom = (round(self.pos.x), round(self.pos.y))
        self.pos = pygame.math.Vector2(self.hitbox.midbottom)
        self.rect.midbottom = self.hitbox.midbottom