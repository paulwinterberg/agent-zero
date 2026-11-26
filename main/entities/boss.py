import settings

from entities.character_sprite import load_character_frame
from entities.enemy import Enemy


class BossEnemy(Enemy):
    PHASES = (
        (200.0, settings.PISTOL_COOLDOWN * 2),
        (250.0, settings.PISTOL_COOLDOWN * 1.5),
        (200.0, settings.PISTOL_COOLDOWN),
    )
    MINION_SPAWN_INTERVAL = 30.0

    def __init__(self, pos, tool_manager=None, spawn_minions=None):
        super().__init__(pos, tool_manager=tool_manager)
        self.image = load_character_frame("AgentX.png", (128, 128), (48, 56))
        self.base_image = self.image.copy()
        self.rect = self.image.get_rect(midbottom=self.hitbox.midbottom)
        self.phase = 1
        self.spawn_minions = spawn_minions
        self.phase_spawn_elapsed = 0.0
        self._set_phase(1)

    def _set_phase(self, phase):
        self.phase = phase
        self.max_health, self.fire_cooldown = self.PHASES[phase - 1]
        self.health = self.max_health
        if self.tool is not None:
            self.tool.shot_cooldown = self.fire_cooldown

    def take_damage(self, dmg):
        if self.dead:
            return

        self.health = max(0, self.health - dmg)
        if self.health > 0:
            return

        if self.phase < len(self.PHASES):
            self._set_phase(self.phase + 1)
            self.phase_spawn_elapsed = 0.0
        else:
            self.die()

    def update(self, dt):
        super().update(dt)
        if self.dead or self.phase != 3:
            return

        self.phase_spawn_elapsed += dt
        while self.phase_spawn_elapsed >= self.MINION_SPAWN_INTERVAL:
            self.phase_spawn_elapsed -= self.MINION_SPAWN_INTERVAL
            if self.spawn_minions is not None:
                self.spawn_minions(self)
