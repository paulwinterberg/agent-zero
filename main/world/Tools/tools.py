import pygame
import settings


class Tools:
    """Basisklasse für Mission-Tools."""

    def __init__(self):
        self.name = None
        self.state = None
        self.collected = False
        self.equipped = False
        self.held_sprite = None

    def on_interact(self):
        if self.collected:
            return False

        self.collected = True
        self.equipped = True
        self.state = "equipped"
        self.sprite.kill()
        return True

    def drop(self, position):
        self.collected = False
        self.equipped = False
        self.state = "ready"
        if self.held_sprite:
            self.held_sprite.kill()
            self.held_sprite = None
        self.sprite.rect.center = position

    def create_held_sprite(self):
        width, height = self.sprite.image.get_size()
        scale = min(16 / width, 16 / height)
        held_size = (max(1, round(width * scale)), max(1, round(height * scale)))
        self.held_sprite = pygame.sprite.Sprite()
        self.held_sprite.image = pygame.transform.scale(self.sprite.image, held_size)
        self.held_sprite.rect = self.held_sprite.image.get_rect()
        return self.held_sprite


class MissionToolManager:
    """Verwaltet Mission-Tools, Inventar, Eingaben und Projektile."""

    def __init__(self, sprite_group, tilemap, interaction_range=50):
        self.tools = []
        self.inventory = []
        self.sprite_group = sprite_group
        self.tilemap = tilemap
        self.interaction_range = interaction_range
        self.interaction_cooldown = 0
        self.interaction_cooldown_time = 0.3
        self.nearby_tools = []

    def add_tool(self, tool):
        """Fügt ein Tool mit passender Tiefensortierung zur Welt hinzu."""
        self.tools.append(tool)
        self.sprite_group.add(
            tool.sprite,
            layer=self.tilemap.y_sort_layer(tool.sprite.rect.bottom),
        )

    def add_demo_tools(self, player):
        """Platziert die aktuell verfügbaren Mission-Tools im Testlevel."""
        from world.Tools.pistol import Pistol
        from world.Tools.red_block import RedBlock
        from world.Tools.taser import Taser

        tools = (
            Taser((player.rect.centerx + 40, player.rect.centery)),
            RedBlock((player.rect.centerx + 80, player.rect.centery)),
            Pistol((player.rect.centerx + 120, player.rect.centery)),
        )
        tools[1].name = "Blue Block"
        tools[1].sprite.image.fill((40, 100, 255))
        for tool in tools:
            self.add_tool(tool)

    def update(self, dt, player):
        self.interaction_cooldown = max(0, self.interaction_cooldown - dt)
        self.update_projectiles(dt)
        self.update_held_visual(player)
        player_center = pygame.Vector2(player.rect.center)
        self.nearby_tools = [
            tool for tool in self.tools
            if not tool.collected
            and player_center.distance_to(tool.sprite.rect.center) <= self.interaction_range
        ]
        self.nearby_tools.sort(
            key=lambda tool: player_center.distance_to(tool.sprite.rect.center)
        )

    def handle_event(self, event, player):
        if event.type == pygame.KEYDOWN and event.key == settings.TOOL_PICKUP:
            return self.try_interact(player)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            map_layer = getattr(self.sprite_group, "_map_layer", None)
            screen = pygame.display.get_surface()
            screen_center = pygame.Vector2(screen.get_rect().center) if screen else pygame.Vector2()
            zoom = map_layer.zoom if map_layer else 1
            mouse_delta = (pygame.Vector2(event.pos) - screen_center) / zoom
            target = pygame.Vector2(player.rect.center) + mouse_delta
            return self.use_primary(player, target)
        return False

    def try_interact(self, player):
        if not self.nearby_tools or self.interaction_cooldown > 0:
            return False

        self.interaction_cooldown = self.interaction_cooldown_time
        tool = self.nearby_tools[0]
        if tool.on_interact():
            if self.inventory:
                previous_tool = self.inventory[0]
                previous_tool.drop(player.rect.center)
                self.sprite_group.add(
                    previous_tool.sprite,
                    layer=self.tilemap.y_sort_layer(previous_tool.sprite.rect.bottom),
                )

            self.inventory[:] = [tool]
            self.add_held_visual(tool, player)
            return True
        return False

    def add_held_visual(self, tool, player):
        held_sprite = tool.create_held_sprite()
        self.sprite_group.add(
            held_sprite,
            layer=self.tilemap.y_sort_layer(player.rect.bottom) + 1,
        )
        self.update_held_visual(player)

    def update_held_visual(self, player):
        if self.inventory and self.inventory[0].held_sprite:
            held_sprite = self.inventory[0].held_sprite
            direction = pygame.Vector2(1, 0)
            screen = pygame.display.get_surface()
            if screen:
                mouse_delta = pygame.Vector2(pygame.mouse.get_pos()) - pygame.Vector2(screen.get_rect().center)
                if mouse_delta.length_squared() > 0:
                    direction = mouse_delta.normalize()

            orbit_position = pygame.Vector2(player.rect.center) + direction * 18
            center = round(orbit_position.x), round(orbit_position.y)
            held_sprite.rect = held_sprite.image.get_rect(center=center)
            self.sprite_group.change_layer(
                held_sprite,
                self.tilemap.y_sort_layer(player.rect.bottom) + 1,
            )

    def use_primary(self, player, target):
        """Verwendet das aktuell ausgerüstete Tool mit Linksklick."""
        if not self.inventory or not hasattr(self.inventory[0], "fire"):
            return False

        projectile = self.inventory[0].fire(
            player.rect.center,
            target,
            self.tilemap,
        )
        self.sprite_group.add(
            projectile.sprite,
            layer=self.tilemap.y_sort_layer(projectile.sprite.rect.bottom),
        )
        return True

    def update_projectiles(self, dt):
        """Bewegt Kugeln und entfernt abgelaufene Sprites."""
        for sprite in list(self.sprite_group.sprites()):
            projectile = getattr(sprite, "projectile", None)
            if projectile and not projectile.update(dt):
                sprite.kill()