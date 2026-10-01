import pygame
import settings
import math


class Tools:
    """Basisklasse für Mission-Tools."""

    def __init__(self):
        self.name = None
        self.anzahl = 1
        self.consumable = False
        self.keep_when_empty = False
        self.state = None
        self.collected = False
        self.equipped = False
        self.held_sprite = None

    def on_interact(self):
        if self.collected or (self.anzahl <= 0 and not self.keep_when_empty):
            return False

        self.collected = True
        self.equipped = True
        self.state = "equipped"
        self.sprite.kill()
        return True

    def consume(self):
        """Verbraucht eine Ladung und entfernt das Tool bei Anzahl null."""
        if self.anzahl <= 0:
            return False

        self.anzahl -= 1
        if self.anzahl == 0:
            if self.keep_when_empty:
                self.state = "empty"
                return True

            self.state = "consumed"
            self.collected = False
            self.equipped = False
            if self.held_sprite:
                self.held_sprite.kill()
                self.held_sprite = None
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
        self.max_inventory_slots = settings.WEAPON_WHEEL_SLOTS
        self.selected_slot = 0
        self.active_slot = 0
        self.weapon_wheel_open = False

    @property
    def current_tool(self):
        if not self.inventory or self.active_slot >= len(self.inventory):
            return None
        return self.inventory[self.active_slot]

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
        from world.Tools.key import Key
        from world.Tools.smoke_bomb import SmokeBomb
        from world.Tools.munition import Munition
        from world.Tools.energie import Energie

        tools = (
            Taser((player.rect.centerx + 40, player.rect.centery)),
            RedBlock((player.rect.centerx + 80, player.rect.centery)),
            Pistol((player.rect.centerx + 120, player.rect.centery)),
            Key((player.rect.centerx + 160, player.rect.centery)),
            SmokeBomb((player.rect.centerx + 200, player.rect.centery)),
            Munition((player.rect.centerx + 240, player.rect.centery)),
            Energie((player.rect.centerx + 280, player.rect.centery)),
        )
        tools[1].name = "Blue Block"
        tools[1].sprite.image.fill((40, 100, 255))
        for tool in tools:
            self.add_tool(tool)

    def update(self, dt, player):
        self.interaction_cooldown = max(0, self.interaction_cooldown - dt)
        self.update_projectiles(dt)
        if self.weapon_wheel_open:
            self.select_slot_at(pygame.mouse.get_pos())
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
        if event.type == pygame.KEYDOWN and event.key == settings.WEAPON_WHEEL_TOGGLE:
            self.weapon_wheel_open = True
            return True
        if event.type == pygame.KEYUP and event.key == settings.WEAPON_WHEEL_TOGGLE:
            self.weapon_wheel_open = False
            self.set_active_slot(self.selected_slot, player)
            return True
        if self.weapon_wheel_open:
            if event.type == pygame.MOUSEMOTION:
                self.select_slot_at(event.pos)
            elif event.type == pygame.MOUSEWHEEL:
                self.cycle_selected_slot(event.y)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button in (1, 3):
                self.select_slot_at(event.pos)
                self.weapon_wheel_open = False
                self.set_active_slot(self.selected_slot, player)
            return False
        if event.type == pygame.KEYDOWN and event.key == settings.TOOL_DROP:
            return self.drop_current_tool(player)
        if event.type == pygame.KEYDOWN and event.key == settings.TOOL_RELOAD:
            return self.reload_current_tool()
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
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            map_layer = getattr(self.sprite_group, "_map_layer", None)
            screen = pygame.display.get_surface()
            screen_center = pygame.Vector2(screen.get_rect().center) if screen else pygame.Vector2()
            zoom = map_layer.zoom if map_layer else 1
            mouse_delta = (pygame.Vector2(event.pos) - screen_center) / zoom
            target = pygame.Vector2(player.rect.center) + mouse_delta
            return self.use_secondary(player, target)
        return False

    def drop_current_tool(self, player):
        """Legt das aktuell gehaltene Tool an der Spielerposition ab."""
        tool = self.current_tool
        if not tool:
            return False

        self.inventory.pop(self.active_slot)
        tool.drop(player.rect.center)
        self.sprite_group.add(
            tool.sprite,
            layer=self.tilemap.y_sort_layer(tool.sprite.rect.bottom),
        )
        self.active_slot = min(self.active_slot, max(0, len(self.inventory) - 1))
        self.selected_slot = self.active_slot
        if self.current_tool:
            self.add_held_visual(self.current_tool, player)
        return True

    def try_interact(self, player):
        if not self.nearby_tools or self.interaction_cooldown > 0:
            return False

        self.interaction_cooldown = self.interaction_cooldown_time
        tool = self.nearby_tools[0]
        if getattr(tool, "refill_tool_name", None):
            if tool.name in ("Munition", "Energie"):
                return self.collect_reload_pickup(tool)
            return self.collect_refill(tool)
        if len(self.inventory) >= self.max_inventory_slots:
            return False

        if tool.on_interact():
            slot = len(self.inventory)
            self.inventory.append(tool)

            self.set_active_slot(slot, player)
            return True
        return False

    def collect_refill(self, refill):
        """Nimmt ein Munitions- oder Energie-Pickup auf."""
        target = self.current_tool
        if not target or target.name != refill.refill_tool_name:
            return False

        if not target or not refill.on_interact():
            return False

        target.anzahl += refill.refill_amount
        return True

    def collect_ammo_pickup(self, pickup):
        """Nimmt Munition als Reserve-Stack ins Inventar auf."""
        return self.collect_reload_pickup(pickup)

    def collect_reload_pickup(self, pickup):
        """Nimmt Munition oder Energie auf und lädt das passende Tool."""
        reserve = next(
            (tool for tool in self.inventory if tool.name == pickup.name),
            None,
        )

        current = self.current_tool
        if current and getattr(current, "reload_item_name", None) == pickup.name:
            missing = current.max_anzahl - current.anzahl
            loaded = min(missing, pickup.refill_amount)
            remaining = pickup.refill_amount - loaded
            if remaining and not reserve and len(self.inventory) >= self.max_inventory_slots:
                return False
            if not pickup.on_interact():
                return False

            current.anzahl += loaded
            if remaining:
                if reserve:
                    reserve.anzahl += remaining
                else:
                    pickup.anzahl = remaining
                    self.inventory.append(pickup)
            return True

        if reserve:
            reserve.anzahl += pickup.refill_amount
            pickup.on_interact()
            return True

        if len(self.inventory) >= self.max_inventory_slots:
            return False
        if not pickup.on_interact():
            return False

        pickup.anzahl = pickup.refill_amount
        self.inventory.append(pickup)
        return True

    def reload_current_tool(self):
        """Lädt das gehaltene Tool aus einem passenden Reserve-Stack."""
        tool = self.current_tool
        if not tool or not getattr(tool, "reload_item_name", None):
            return False

        maximum = getattr(tool, "max_anzahl", tool.anzahl)
        missing = maximum - tool.anzahl
        if missing <= 0:
            return False

        reserve_index = next(
            (
                index for index, item in enumerate(self.inventory)
                if item.name == tool.reload_item_name and item.anzahl > 0
            ),
            None,
        )
        if reserve_index is None:
            return False

        reserve = self.inventory[reserve_index]
        loaded = min(missing, reserve.anzahl)
        tool.anzahl += loaded
        reserve.anzahl -= loaded
        if reserve.anzahl == 0:
            self.remove_inventory_slot(reserve_index)
        return True

    def remove_inventory_slot(self, slot):
        self.inventory.pop(slot)
        if not self.inventory:
            self.active_slot = 0
            self.selected_slot = 0
            return
        if slot < self.active_slot:
            self.active_slot -= 1
        self.active_slot = min(self.active_slot, len(self.inventory) - 1)
        self.selected_slot = self.active_slot

    def add_held_visual(self, tool, player):
        if tool.held_sprite:
            tool.held_sprite.kill()
        held_sprite = tool.create_held_sprite()
        self.sprite_group.add(
            held_sprite,
            layer=self.tilemap.y_sort_layer(player.rect.bottom),
        )
        self.update_held_visual(player)

    def set_active_slot(self, slot, player):
        if self.current_tool and self.current_tool.held_sprite:
            self.current_tool.held_sprite.kill()
            self.current_tool.held_sprite = None
        self.active_slot = max(0, min(slot, len(self.inventory) - 1))
        self.selected_slot = self.active_slot
        if self.current_tool:
            self.add_held_visual(self.current_tool, player)

    def select_slot_at(self, position):
        screen = pygame.display.get_surface()
        if not screen or not self.inventory:
            return

        center = pygame.Vector2(screen.get_rect().center)
        offset = pygame.Vector2(position) - center
        if offset.length_squared() < 35 ** 2:
            return

        cursor_angle = math.atan2(offset.y, offset.x)
        best_slot = None
        best_distance = math.inf
        for slot in range(min(self.max_inventory_slots, len(self.inventory))):
            slot_angle = -math.pi / 2 - slot * (math.pi * 2 / self.max_inventory_slots)
            angle_distance = abs(
                math.atan2(
                    math.sin(cursor_angle - slot_angle),
                    math.cos(cursor_angle - slot_angle),
                )
            )
            if angle_distance < best_distance:
                best_slot = slot
                best_distance = angle_distance

        if best_slot is not None:
            self.selected_slot = best_slot

    def cycle_selected_slot(self, direction):
        if not self.inventory:
            return

        step = -1 if direction > 0 else 1
        self.selected_slot = (self.selected_slot + step) % len(self.inventory)

    def update_held_visual(self, player):
        if self.current_tool and self.current_tool.held_sprite:
            held_sprite = self.current_tool.held_sprite
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
                self.tilemap.y_sort_layer(player.rect.bottom),
            )

    def use_primary(self, player, target):
        """Verwendet das aktuell ausgerüstete Tool mit Linksklick."""
        if (
            not self.current_tool
            or not hasattr(self.current_tool, "fire")
            or self.current_tool.anzahl <= 0
        ):
            return False

        tool = self.current_tool
        projectile = tool.fire(
            player.rect.center,
            target,
            self.tilemap,
        )
        self.sprite_group.add(
            projectile.sprite,
            layer=self.tilemap.y_sort_layer(projectile.sprite.rect.bottom),
        )
        if tool.consumable:
            tool.consume()
        if tool.anzahl <= 0 and not tool.keep_when_empty:
            self.inventory.pop(self.active_slot)
            self.active_slot = min(self.active_slot, max(0, len(self.inventory) - 1))
            self.selected_slot = self.active_slot
        return True

    def use_secondary(self, player, target):
        """Verwendet ein Tool mit Rechtsklick."""
        if (
            not self.current_tool
            or not getattr(self.current_tool, "secondary_use", False)
            or self.current_tool.anzahl <= 0
        ):
            return False

        tool = self.current_tool
        projectile = tool.fire(player.rect.center, target, self.tilemap)
        self.sprite_group.add(
            projectile.sprite,
            layer=self.tilemap.y_sort_layer(projectile.sprite.rect.bottom),
        )
        if tool.consumable:
            tool.consume()
        if tool.anzahl <= 0 and not tool.keep_when_empty:
            self.inventory.pop(self.active_slot)
            self.active_slot = min(self.active_slot, max(0, len(self.inventory) - 1))
            self.selected_slot = self.active_slot
        return True

    def update_projectiles(self, dt):
        """Bewegt Kugeln und entfernt abgelaufene Sprites."""
        for sprite in list(self.sprite_group.sprites()):
            projectile = getattr(sprite, "projectile", None)
            if projectile and not projectile.update(dt):
                effect = getattr(projectile, "on_expire", lambda: None)()
                sprite.kill()
                if effect:
                    self.sprite_group.add(
                        effect.sprite,
                        layer=self.tilemap.y_sort_layer(effect.sprite.rect.bottom),
                    )