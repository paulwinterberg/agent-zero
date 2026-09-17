import pygame

from world.Tools.tools import Tools


class RedBlock(Tools):
    """Ein einfacher roter Test-Block zum Aufheben."""

    def __init__(self, position):
        super().__init__()
        self.name = "Red Block"
        self.state = "ready"
        self.collected = False
        self.equipped = False
        self.sprite = pygame.sprite.Sprite()
        self.sprite.image = pygame.Surface((32, 32))
        self.sprite.image.fill((255, 40, 40))
        pygame.draw.rect(self.sprite.image, (255, 255, 255), self.sprite.image.get_rect(), 3)
        self.sprite.rect = self.sprite.image.get_rect(center=position)

    def on_interact(self):
        if self.collected:
            return False

        self.collected = True
        self.equipped = True
        self.state = "equipped"
        self.sprite.kill()
        print(f"Mission-Tool aufgehoben: {self.name}")
        return True


class MissionToolManager:
    """Verwaltet sammelbare Mission-Tools unabhängig von Kollisionen."""

    def __init__(self, interaction_range=50):
        self.tools = []
        self.inventory = []
        self.interaction_range = interaction_range
        self.interaction_cooldown = 0
        self.interaction_cooldown_time = 0.3
        self.nearby_tools = []

    def add_tool(self, tool, sprite_group, layer):
        """Fügt ein Tool zur Welt und zur Tool-Verwaltung hinzu."""
        self.tools.append(tool)
        sprite_group.add(tool.sprite, layer=layer)

    def update(self, dt, player):
        self.interaction_cooldown = max(0, self.interaction_cooldown - dt)
        player_center = pygame.Vector2(player.rect.center)
        self.nearby_tools = [
            tool for tool in self.tools
            if not tool.collected
            and player_center.distance_to(tool.sprite.rect.center) <= self.interaction_range
        ]
        self.nearby_tools.sort(
            key=lambda tool: player_center.distance_to(tool.sprite.rect.center)
        )

    def try_interact(self):
        if not self.nearby_tools or self.interaction_cooldown > 0:
            return False

        self.interaction_cooldown = self.interaction_cooldown_time
        tool = self.nearby_tools[0]
        if tool.on_interact():
            self.inventory.append(tool)
            return True
        return False
