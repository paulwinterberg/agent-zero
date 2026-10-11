import math

import pygame
import pygame_gui
import settings

from entities.player.player import Player
from states.state import State
from core.renderer import load_tilemap, render_world, get_ui_manager
from core.interactions import InteractionManager
from world.Tools.tools import MissionToolManager


TUTORIAL_MESSAGES = {
    "ContainermapStart": (
        "Willkommen auf dem Containerschiff. Suche das Kokain, das die "
        "Schmuggler hier schmuggeln, und fliehe mit den Beweismitteln. "
        "Gehe nun nach links zur ersten Kreuzung und suche den grünen "
        "Container dort am Rand."
    ),
    "OpenContainer": (
        "Mit F kannst du den Container öffnen, falls er nicht verschlossen "
        "ist. Für die verschlossenen brauchst du einen Schlüssel, den du in "
        "einem gelben Container findest. Insgesamt gibt es 8 Container, die "
        "du öffnen kannst. Danach suchst du nach dem Knopf, der die "
        "Eisentür zur Kommandostelle öffnet."
    ),
    "PressTheButton": (
        "Drücke den Knopf, damit die verschlossene Eisentür zur "
        "Kommandostelle aufspringt."
    ),
    "Komandostelle": (
        "Finde die 2 verborgenen Knöpfe, um die vorletzte Ebene "
        "freizuschalten. Viel Glück!"
    ),
    "NextStep": (
        "Fast geschafft! Du musst nur noch 2 Knöpfe finden und du bist "
        "fertig. Probiere nicht, getötet zu werden."
    ),
    "Brücke": (
        "Auf der Brücke wird das ganze Schiff gesteuert. Finde den Knopf, "
        "der hier verborgen ist."
    ),
    "FindExit": (
        "Nur noch ein letzter Schritt. Du bist schon ganz nah. Töte die "
        "Wachen und steig in den Container, um als blinder Passagier das "
        "Schiff zu verlassen."
    ),
}

COMPLETION_TUTORIAL_NAME = "ContainermapEnd"
COMPLETION_FADE_DURATION = 1.0
COMPLETION_MESSAGE_DURATION = 3.0
COMPLETION_REWARD = 800


class Gameplay(State):
    def __init__(self, initial_money=0):
        self.player = Player()
        self.tilemap, self.group = load_tilemap("assets/levels/containership.tmx", self.player)
        self.interaction_manager = InteractionManager()
        self.tool_manager = MissionToolManager(self.group, self.tilemap)
        self.tool_manager.money = initial_money
        
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
        self.tutorial_active = False
        self.money_font = pygame.font.Font("assets/fonts/PixelifySans-Medium.ttf", 22)
        self.tutorial_trigger_radius = 48
        self.shown_tutorials = set()
        self.completion_started = False
        self.completion_elapsed = 0
        self.completion_rewarded = False
        self.tutorial_points = {
            name: point
            for name in (*TUTORIAL_MESSAGES, COMPLETION_TUTORIAL_NAME)
            if (point := self.tilemap.get_object("Tutorial", name)) is not None
        }
        self.interaction_feedback_font = pygame.font.Font(
            "assets/fonts/PixelifySans-Medium.ttf", 22
        )
    
    def update(self, dt, events):
        if self.completion_started:
            self._update_completion(dt)
            return

        if self.tutorial_active:
            if any(
                event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN
                for event in events
            ):
                self.tutorial_active = False
                self.interaction_feedback = ""
                self.interaction_feedback_timer = 0
            return

        self.interaction_feedback_timer = max(
            0, self.interaction_feedback_timer - dt
        )
        self._update_tutorial_feedback()
        if self.tutorial_active or self.completion_started:
            return

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

    def _update_tutorial_feedback(self):
        player_position = pygame.Vector2(self.player.rect.center)
        for name, point in self.tutorial_points.items():
            if name in self.shown_tutorials:
                continue
            if player_position.distance_to((point.x, point.y)) > self.tutorial_trigger_radius:
                continue

            self.shown_tutorials.add(name)
            if name == COMPLETION_TUTORIAL_NAME:
                self.completion_started = True
                self.interaction_feedback_timer = 0
                return
            self.interaction_feedback = TUTORIAL_MESSAGES[name]
            self.tutorial_active = True
            self.interaction_feedback_timer = 0
            return

    def _update_completion(self, dt):
        self.completion_elapsed += dt
        if (
            self.completion_elapsed >= COMPLETION_FADE_DURATION
            and not self.completion_rewarded
        ):
            self.tool_manager.money += COMPLETION_REWARD
            self.completion_rewarded = True

        if self.completion_elapsed >= COMPLETION_FADE_DURATION + COMPLETION_MESSAGE_DURATION:
            from states.main_menu import MainMenu
            from core import game

            self.stamina_bar.hide()
            self.ammo_label.hide()
            game.state_manager.pop()
            game.state_manager.push(MainMenu(money=self.tool_manager.money))
    
    def draw(self, screen, dt):
        render_world(dt, self.tilemap, self.group, self.player)
        self._draw_money_counter(screen)
        if self.tool_manager.weapon_wheel_open:
            self._draw_weapon_wheel(screen)
        if self.interaction_feedback_timer > 0 or self.tutorial_active:
            self._draw_interaction_feedback(screen)
        if self.completion_started:
            self._draw_completion(screen)

    def _draw_completion(self, screen):
        alpha = min(255, round(255 * self.completion_elapsed / COMPLETION_FADE_DURATION))
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, alpha))
        screen.blit(overlay, (0, 0))

        if self.completion_elapsed >= COMPLETION_FADE_DURATION:
            message = self.interaction_feedback_font.render(
                "Du hast es geschafft...", True, (255, 255, 255)
            )
            reward = self.money_font.render(
                f"+{COMPLETION_REWARD} Geld", True, (255, 219, 88)
            )
            screen.blit(message, message.get_rect(center=screen.get_rect().center))
            screen.blit(
                reward,
                reward.get_rect(
                    center=(screen.get_width() // 2, screen.get_height() // 2 + 48)
                ),
            )

    def _draw_money_counter(self, screen):
        money_text = self.money_font.render(f"$ {self.tool_manager.money}", True, (255, 219, 88))
        panel = pygame.Surface((money_text.get_width() + 24, money_text.get_height() + 14), pygame.SRCALPHA)
        pygame.draw.rect(panel, (20, 25, 29, 200), panel.get_rect(), border_radius=6)
        pygame.draw.rect(panel, (255, 219, 88), panel.get_rect(), 2, border_radius=6)
        panel_rect = panel.get_rect(topright=(screen.get_width() - 20, 20))
        screen.blit(panel, panel_rect)
        screen.blit(money_text, money_text.get_rect(center=panel_rect.center))

    def _draw_interaction_feedback(self, screen):
        max_text_width = max(1, min(900, screen.get_width() - 64))
        lines = []
        current_line = ""
        for word in self.interaction_feedback.split():
            candidate = f"{current_line} {word}".strip()
            if (
                current_line
                and self.interaction_feedback_font.size(candidate)[0] > max_text_width
            ):
                lines.append(current_line)
                current_line = word
            else:
                current_line = candidate
        if current_line:
            lines.append(current_line)
        if self.tutorial_active:
            lines.append("Drücke ENTER zum Fortfahren")

        line_height = self.interaction_feedback_font.get_linesize()
        text = pygame.Surface(
            (
                max(self.interaction_feedback_font.size(line)[0] for line in lines),
                line_height * len(lines),
            ),
            pygame.SRCALPHA,
        )
        for index, line in enumerate(lines):
            rendered_line = self.interaction_feedback_font.render(
                line, True, (255, 255, 255)
            )
            text.blit(rendered_line, (0, index * line_height))

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

        