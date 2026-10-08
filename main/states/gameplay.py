import math

import pygame
import pygame_gui
import settings

from entities.player.player import Player
from states.state import State
from core.renderer import load_tilemap, render_world, get_ui_manager
from core.interactions import InteractionManager
from world.Tools.tools import MissionToolManager

class Gameplay(State):
    def __init__(self):
        self.player = Player()
        self.tilemap, self.group = load_tilemap("assets/levels/containership.tmx", self.player)
        self.interaction_manager = InteractionManager()
        self.tool_manager = MissionToolManager(self.group, self.tilemap)
        
        self.tilemap.zoom_to(4)
        
        spawnPoint = self.tilemap.get_object("Spawns", "PlayerSpawn")
        self.player.goto((spawnPoint.x, spawnPoint.y))

        self.tool_manager.spawn_tools_from_map()

        self.stamina_bar = pygame_gui.elements.UIProgressBar(
            relative_rect=pygame.Rect((20, 20), (200, 25)),
            manager=get_ui_manager(),
        )
        self.ammo_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((20, 50), (220, 30)),
            text="",
            manager=get_ui_manager(),
        )
        self.ammo_label.hide()
        self.interaction_feedback = ""
        self.interaction_feedback_timer = 0
        self.interaction_feedback_font = pygame.font.Font(
            "assets/fonts/PixelifySans-Medium.ttf", 22
        )
    
    def update(self, dt, events):
        self.interaction_feedback_timer = max(
            0, self.interaction_feedback_timer - dt
        )
        self.player.update(dt, self.tilemap)
        self.interaction_manager.update(dt, self.player, self.tilemap)

        self.stamina_bar.set_current_progress(self.player.get_stamina_percent() * 100.0)
        
        self.tool_manager.update(dt, self.player)
        self._update_ammo_label()
        
        for event in events:
            self.tool_manager.handle_event(event, self.player)
            if event.type == pygame.KEYDOWN and event.key == settings.INTERACT:
                held_tool = self.tool_manager.current_tool
                self.interaction_manager.try_interact(held_tool)
                if self.interaction_manager.feedback_message:
                    self.interaction_feedback = (
                        self.interaction_manager.feedback_message
                    )
                    self.interaction_feedback_timer = 2
    
    def draw(self, screen, dt):
        render_world(dt, self.tilemap, self.group, self.player)
        if self.tool_manager.weapon_wheel_open:
            self._draw_weapon_wheel(screen)
        if self.interaction_feedback_timer > 0:
            self._draw_interaction_feedback(screen)

    def _draw_interaction_feedback(self, screen):
        text = self.interaction_feedback_font.render(
            self.interaction_feedback, True, (255, 255, 255)
        )
        padding = 18
        panel = pygame.Surface(
            (text.get_width() + padding * 2, text.get_height() + 16),
            pygame.SRCALPHA,
        )
        pygame.draw.rect(
            panel, (20, 25, 29, 225), panel.get_rect(), border_radius=5
        )
        accent = (240, 180, 75) if "verschlossen" in self.interaction_feedback else (95, 205, 145)
        pygame.draw.rect(panel, accent, panel.get_rect(), 2, border_radius=5)
        panel_rect = panel.get_rect(
            midbottom=(screen.get_width() // 2, screen.get_height() - 32)
        )
        screen.blit(panel, panel_rect)
        screen.blit(text, text.get_rect(center=panel_rect.center))

    def _update_ammo_label(self):
        held_tool = self.tool_manager.current_tool
        if held_tool and held_tool.name == "Pistol":
            self.ammo_label.set_text(f"Pistol: {held_tool.anzahl} Schuss")
            self.ammo_label.show()
        elif held_tool and held_tool.name == "Taser":
            self.ammo_label.set_text(f"Taser: {held_tool.anzahl} Energie")
            self.ammo_label.show()
        else:
            self.ammo_label.hide()

    def _draw_weapon_wheel(self, screen):
        center = pygame.Vector2(screen.get_rect().center)
        radius = 125
        slot_radius = 34
        font = pygame.font.Font(None, 18)
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 90))
        screen.blit(overlay, (0, 0))

        for slot in range(self.tool_manager.max_inventory_slots):
            angle = slot * (2 * math.pi / self.tool_manager.max_inventory_slots)
            position = center + pygame.Vector2(0, -radius).rotate(
                -math.degrees(angle)
            )
            active = slot == self.tool_manager.selected_slot
            color = (80, 180, 110) if active else (55, 60, 70)
            pygame.draw.circle(screen, color, position, slot_radius)
            pygame.draw.circle(screen, (220, 225, 230), position, slot_radius, 2)

            if slot < len(self.tool_manager.inventory):
                tool = self.tool_manager.inventory[slot]
                name = font.render(tool.name or "Tool", True, (255, 255, 255))
                name_rect = name.get_rect(center=(position.x, position.y + 48))
                screen.blit(name, name_rect)
                count = font.render(str(tool.anzahl), True, (255, 230, 120))
                screen.blit(count, count.get_rect(center=position))

        