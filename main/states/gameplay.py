import math

import pygame
import pygame_gui
import settings
import core.state_manager as state_manager

from globals import globs
from core import levels
from entities.player.player import Player
from states.game_state import GameState
from core.renderer import load_tilemap, render_world, get_ui_manager, get_ui_manager
from core.interactions import InteractionManager
from world.tools.tools import MissionToolManager
from world.interactibles.hint import Hint
from enemies.enemy_manager import EnemyManager

class Gameplay(GameState):
    def __init__(self, initial_money=0, level="containership"):
        self.player = Player()
        globs["player"] = self.player
        
        self.tilemap, self.group = load_tilemap("assets/levels/"+level+".tmx", self.player)
        self.interaction_manager = InteractionManager()
        self.interaction_manager.initialize_doors(self.tilemap)
        self.tool_manager = MissionToolManager(self.group, self.tilemap)
        self.tool_manager.money = initial_money
        self.enemy_manager = EnemyManager(
            self.tilemap,
            self.group,
            self.tool_manager,
        )
        
        self.level_meta = levels.LEVELS[level]
        
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
        self.hint_active = False
        self.hint_image = pygame.image.load(
            "tiled/tilesets/Hint.png"
        ).convert_alpha()
        self.money_font = pygame.font.Font("assets/fonts/PixelifySans-Medium.ttf", 22)
        self.tutorial_trigger_radius = 48
        self.shown_tutorials = set()
        self.completion_started = False
        self.completion_elapsed = 0
        self.completion_rewarded = False
        self.tutorial_points = {
            name: point
            for name in (*self.level_meta.MESSAGES, self.level_meta.COMPLETION_TUTORIAL_NAME)
            if (point := self.tilemap.get_object("Tutorial", name)) is not None
        }
        self.interaction_feedback_font = pygame.font.Font(
            "assets/fonts/PixelifySans-Medium.ttf", 22
        )

    def exit(self):
        self.stamina_bar.hide()
        self.ammo_label.hide()
    
    def update(self, dt, events):
        if self.player.dead:
            from states.main_menu import MainMenu

            state_manager.pop()
            state_manager.push(MainMenu())
            return

        if self.completion_started:
            self._update_completion(dt)
            return

        if self.hint_active:
            if any(
                event.type == pygame.KEYDOWN
                and event.key in (pygame.K_RETURN, pygame.K_KP_ENTER)
                for event in events
            ):
                hint = self.interaction_manager.get_interactible_instance("Hint")
                if isinstance(hint, Hint):
                    hint.close()
                self.hint_active = False
            return

        if self.tutorial_active:
            if any(
                event.type == pygame.KEYDOWN
                and event.key in (pygame.K_RETURN, pygame.K_KP_ENTER)
                for event in events
            ):
                self.tutorial_active = False
                self.interaction_feedback = ""
                self.interaction_feedback_timer = 0
            return

        self.interaction_feedback_timer = max(
            0, self.interaction_feedback_timer - dt
        )
        if self.interaction_feedback_timer == 0:
            self.interaction_feedback = ""

        self.enemy_manager.update(dt)
        self.player.update(dt, self.tilemap)
        self._update_tutorial_feedback()
        if self.tutorial_active or self.completion_started:
            return

        self.interaction_manager.update(dt, self.player, self.tilemap)

        self.stamina_bar.set_current_progress(self.player.get_stamina_percent() * 100.0)
        
        self.tool_manager.update(dt, self.player)
        self._update_ammo_label()
        
        for event in events:
            self.tool_manager.handle_event(event, self.player)
            if (
                event.type == pygame.KEYDOWN
                and event.key in (pygame.K_RETURN, pygame.K_KP_ENTER)
                and self._is_hint_nearby()
            ):
                self.interaction_manager.try_interact()
                hint = self.interaction_manager.get_interactible_instance("Hint")
                self.hint_active = isinstance(hint, Hint) and hint.opened
            elif (
                event.type == pygame.KEYDOWN
                and event.key == settings.INTERACT
                and not self._is_hint_nearby()
            ):
                held_tool = self.tool_manager.current_tool
                self.interaction_manager.try_interact(held_tool)
                if self.interaction_manager.feedback_message:
                    self.interaction_feedback = (
                        self.interaction_manager.feedback_message
                    )
                    self.interaction_feedback_timer = 2

    def _is_hint_nearby(self):
        nearest = self.interaction_manager.get_nearest_interaction()
        return (
            nearest is not None
            and nearest["properties"].get("InteractibleClass") == "Hint"
        )

    def _update_tutorial_feedback(self):
        player_position = pygame.Vector2(self.player.rect.center)
        for name, point in self.tutorial_points.items():
            if name in self.shown_tutorials:
                continue
            if player_position.distance_to((point.x, point.y)) > self.tutorial_trigger_radius:
                continue

            self.shown_tutorials.add(name)
            if name ==self.level_meta.COMPLETION_TUTORIAL_NAME:
                self.completion_started = True
                self.interaction_feedback_timer = 0
                return
            self.interaction_feedback = self.level_meta.MESSAGES[name]
            self.tutorial_active = True
            self.interaction_feedback_timer = 0
            return

    def _update_completion(self, dt):
        self.completion_elapsed += dt
        if (
            self.completion_elapsed >=self.level_meta.COMPLETION_FADE_DURATION
            and not self.completion_rewarded
        ):
            self.tool_manager.money += self.level_meta.COMPLETION_REWARD
            self.completion_rewarded = True

        if self.completion_elapsed >= self.level_meta.COMPLETION_FADE_DURATION + self.level_meta.COMPLETION_MESSAGE_DURATION:
            from states.main_menu import MainMenu
            from core import game

            self.stamina_bar.hide()
            self.ammo_label.hide()
            game.state_manager.pop()
            game.state_manager.push(MainMenu(money=self.tool_manager.money))
    
    def draw(self, screen, dt):
        render_world(
            0 if self.hint_active else dt,
            self.tilemap,
            self.group,
            self.player,
        )
        self._draw_money_counter(screen)
        if self.tool_manager.weapon_wheel_open:
            self._draw_weapon_wheel(screen)
        if self.interaction_feedback_timer > 0 or self.tutorial_active:
            self._draw_interaction_feedback(screen)
        if self.completion_started:
            self._draw_completion(screen)
        if self.hint_active:
            self._draw_hint(screen)
        elif self._is_hint_nearby() and not self.tutorial_active:
            self._draw_hint_prompt(screen)

    def _draw_hint_prompt(self, screen):
        text = self.interaction_feedback_font.render(
            "Durchsuchen Enter drücken.", True, (255, 255, 255)
        )
        padding = 16
        panel = pygame.Surface(
            (text.get_width() + padding * 2, text.get_height() + 16),
            pygame.SRCALPHA,
        )
        pygame.draw.rect(panel, (20, 25, 29, 225), panel.get_rect(), border_radius=5)
        pygame.draw.rect(panel, (95, 205, 145), panel.get_rect(), 2, border_radius=5)
        panel_rect = panel.get_rect(
            midbottom=(screen.get_width() // 2, screen.get_height() - 32)
        )
        screen.blit(panel, panel_rect)
        screen.blit(text, text.get_rect(center=panel_rect.center))

    def _draw_hint(self, screen):
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 225))
        screen.blit(overlay, (0, 0))

        max_width = max(1, screen.get_width() - 80)
        max_height = max(1, screen.get_height() - 150)
        scale = min(
            max_width / self.hint_image.get_width(),
            max_height / self.hint_image.get_height(),
        )
        image_size = (
            max(1, round(self.hint_image.get_width() * scale)),
            max(1, round(self.hint_image.get_height() * scale)),
        )
        image = pygame.transform.scale(self.hint_image, image_size)
        screen.blit(
            image,
            image.get_rect(
                center=(screen.get_width() // 2, screen.get_height() // 2 - 24)
            ),
        )

        instruction = self.interaction_feedback_font.render(
            "Enter drücken um zu verlassen", True, (255, 255, 255)
        )
        screen.blit(
            instruction,
            instruction.get_rect(
                center=(screen.get_width() // 2, screen.get_height() - 48)
            ),
        )

    def _draw_completion(self, screen):
        alpha = min(255, round(255 * self.completion_elapsed /self.level_meta.COMPLETION_FADE_DURATION))
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, alpha))
        screen.blit(overlay, (0, 0))

        if self.completion_elapsed >=self.level_meta.COMPLETION_FADE_DURATION:
            message = self.interaction_feedback_font.render(
                "Mission Accomplished...", True, (255, 255, 255)
            )
            reward = self.money_font.render(
                f"+{self.level_meta.COMPLETION_REWARD} Gold", True, (255, 219, 88)
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
            self.ammo_label.set_text(f"Pistol: {held_tool.amount} Schuss")
            self.ammo_label.show()
        elif held_tool and held_tool.name == "Taser":
            self.ammo_label.set_text(f"Taser: {held_tool.amount} Energy")
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
                count = font.render(str(tool.amount), True, (255, 230, 120))
                screen.blit(count, count.get_rect(center=position))

        