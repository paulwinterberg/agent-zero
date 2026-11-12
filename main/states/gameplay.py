import math

import pygame
import pygame_gui
import settings
import core.state_manager as state_manager
from core import audio
from core import screen

from globals import globs
from core import levels
from entities.player.player import Player
from states.game_state import GameState
from core.renderer import load_tilemap, render_world, get_ui_manager, get_ui_manager
from core.interactions import InteractionManager
from world.tools.tools import MissionToolManager
from world.interactibles.hint import Hint
from enemies.enemy_manager import EnemyManager

LEVEL_DISPLAY_NAMES = {
    "tutorial": "Tutorial",
    "containership": "Containership",
    "hq_lobby": "HQ Lobby",
    "testlevel": "Test Level",
}


class Gameplay(GameState):
    LEVEL_OPTIONS = tuple(
        (
            level_name,
            LEVEL_DISPLAY_NAMES.get(
                level_name, level_name.replace("_", " ").title()
            ),
        )
        for level_name in levels.LEVELS
    )

    def __init__(self, initial_money=0, level="containership"):
        self.level_name = level
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
        
        #load ambience sound if existing
        if self.level_meta.AMBIENCE:
            audio.play_sfx(self.level_meta.AMBIENCE, loops=-1, fade_ms=1000)
        
        self.tilemap.zoom_to(4)
        
        spawnPoint = self.tilemap.get_object("Spawns", "PlayerSpawn")
        self.player.goto((spawnPoint.x, spawnPoint.y))

        self.tool_manager.spawn_tools_from_map()

        self.stamina_bar = pygame_gui.elements.UIProgressBar(
            relative_rect=pygame.Rect((20, 20), (200, 25)),
            manager=get_ui_manager(),
            object_id=pygame_gui.core.ObjectID(class_id="@stamina_bar")
        )
        self.health_bar = pygame_gui.elements.UIProgressBar(
            relative_rect=pygame.Rect((20, screen.get_screen_size()[1] - 45), (200 , 25)),
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
        self.small_font = pygame.font.Font("assets/fonts/PixelifySans-Medium.ttf", 26)
        self.tutorial_trigger_radius = 48
        self.shown_tutorials = set()
        self.completion_started = False
        self.completion_elapsed = 0
        self.completion_rewarded = False
        self.pause_menu_active = False
        self.pause_page = "main"
        self.pause_menu_selected_index = 0
        self.pause_buttons = []
        self.shop_message = ""
        self.death_screen_active = False
        self.continue_button = pygame.Rect(0, 0, 0, 0)
        self.tutorial_points = {
            name: point
            for name in (*self.level_meta.MESSAGES, self.level_meta.COMPLETION_TUTORIAL_NAME)
            if (point := self.tilemap.get_object("Tutorial", name)) is not None
        }
        self.interaction_feedback_font = pygame.font.Font(
            "assets/fonts/PixelifySans-Medium.ttf", 22
        )

    def exit(self):
        self.stamina_bar.kill()
        self.health_bar.kill()
        self.ammo_label.kill()
    
    def update(self, dt, events):
        if self.player.dead:
            if not self.death_screen_active:
                self.death_screen_active = True
                self.pause_menu_active = False
                self.stamina_bar.hide()
                self.health_bar.hide()
                self.ammo_label.hide()
            self._update_death_screen(events)
            return

        if self.pause_menu_active:
            self._update_pause_menu(events)
            return

        if self.completion_started:
            self._update_completion(dt, events)
            return

        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.pause_menu_active = True
                self.pause_page = "main"
                self.pause_menu_selected_index = 0
                self._layout_pause_buttons(pygame.display.get_surface().get_size())
                return

        if self.hint_active:
            if any(
                event.type == pygame.KEYDOWN
                and event.key == pygame.K_SPACE
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
                and event.key == pygame.K_SPACE
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
        self.health_bar.set_current_progress(self.player.get_health_percent() * 100.0)
        
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

    def _is_tutorial_triggered(self, obj, player_position):
        width = getattr(obj, "width", 0) or 0
        height = getattr(obj, "height", 0) or 0
    
        # Rectangle object: trigger when the player's center is inside it
        if width > 0 and height > 0:
            rect = pygame.Rect(obj.x, obj.y, width, height)
            return rect.collidepoint(player_position)
    
        # Point object: trigger when the player is within the trigger radius
        return player_position.distance_to((obj.x, obj.y)) <= self.tutorial_trigger_radius

    def _update_tutorial_feedback(self):
        player_position = pygame.Vector2(self.player.rect.center)
        for name, area in self.tutorial_points.items():
            if name in self.shown_tutorials:
                continue
            if not self._is_tutorial_triggered(area, player_position):
                continue

            self.shown_tutorials.add(name)
            if name == self.level_meta.COMPLETION_TUTORIAL_NAME:
                self.completion_started = True
                self.interaction_feedback_timer = 0
                return
            self.interaction_feedback = self.level_meta.MESSAGES[name]
            self.tutorial_active = True
            self.interaction_feedback_timer = 0

    def _update_completion(self, dt, events):
        self.completion_elapsed += dt
        if (
            self.completion_elapsed >=self.level_meta.COMPLETION_FADE_DURATION
            and not self.completion_rewarded
        ):
            self.tool_manager.money += self.level_meta.COMPLETION_REWARD
            self.completion_rewarded = True

        if (
            self.completion_elapsed
            >= self.level_meta.COMPLETION_FADE_DURATION
            + self.level_meta.COMPLETION_MESSAGE_DURATION
            and any(
                event.type == pygame.KEYDOWN
                and event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE)
                for event in events
            )
        ):
            state_manager.replace(
                Gameplay(initial_money=self.tool_manager.money, level=self.level_name)
            )
    
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
        if self.pause_menu_active:
            self._draw_pause_menu(screen)
        if self.completion_started:
            self._draw_completion(screen)
        if self.death_screen_active:
            self._draw_death_screen(screen)
        if self.hint_active:
            self._draw_hint(screen)
        elif self._is_hint_nearby() and not self.tutorial_active:
            self._draw_hint_prompt(screen)

    def _update_pause_menu(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if self.pause_page == "settings" and event.key in (pygame.K_LEFT, pygame.K_a):
                    audio.set_master_volume(audio.master_volume - 0.1)
                elif self.pause_page == "settings" and event.key in (pygame.K_RIGHT, pygame.K_d):
                    audio.set_master_volume(audio.master_volume + 0.1)
                elif event.key in (pygame.K_UP, pygame.K_w):
                    self.pause_menu_selected_index = (self.pause_menu_selected_index - 1) % len(self.pause_buttons)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.pause_menu_selected_index = (self.pause_menu_selected_index + 1) % len(self.pause_buttons)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self._activate_pause_option(self.pause_menu_selected_index)
                elif event.key == pygame.K_ESCAPE:
                    if self.pause_page == "main":
                        self.pause_menu_active = False
                    else:
                        self.pause_page = "main"
                        self.pause_menu_selected_index = 0
                        self._layout_pause_buttons(pygame.display.get_surface().get_size())
            elif event.type == pygame.MOUSEMOTION:
                for index, rect in enumerate(self.pause_buttons):
                    if rect.collidepoint(event.pos):
                        self.pause_menu_selected_index = index
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for index, rect in enumerate(self.pause_buttons):
                    if rect.collidepoint(event.pos):
                        self._activate_pause_option(index)
                        break

    def _layout_pause_buttons(self, screen_size):
        width, height = screen_size
        button_width = min(420, width - 80)
        labels = self._pause_labels()
        spacing = min(76, (height - 120) / max(1, len(labels) - 1))
        button_height = min(56, spacing - 8)
        x = (width - button_width) // 2
        start_y = max(30, (height - (len(labels) - 1) * spacing - button_height) / 2)
        self.pause_buttons = [
            pygame.Rect(x, round(start_y + offset * spacing), button_width, button_height)
            for offset in range(len(labels))
        ]

    def _activate_pause_option(self, index):
        if self.pause_page == "main":
            if index == 0:
                self.pause_menu_active = False
            elif index == 1:
                self.pause_page = "shop"
                self.pause_menu_selected_index = 0
            elif index == 2:
                self.pause_page = "settings"
                self.pause_menu_selected_index = 0
            elif index == 3:
                self.pause_page = "levels"
                self.pause_menu_selected_index = 0
            elif index == 4:
                state_manager.replace(
                    Gameplay(
                        initial_money=self.tool_manager.money,
                        level=self.level_name,
                    )
                )
        elif self.pause_page == "shop":
            if index == 0:
                success = self.tool_manager.purchase_ammo()
                self.shop_message = (
                    "Munition gekauft." if success
                    else "Nicht genug Coins oder kein Inventarplatz."
                )
            elif index in (1, 2, 3):
                from world.tools.pistol import Pistol

                if index == 1:
                    weapon = Pistol(self.player.rect.center)
                    cost = 400
                elif index == 2:
                    weapon = Pistol(
                        self.player.rect.center,
                        name="Pistol+",
                        shot_cooldown=settings.PISTOL_COOLDOWN / 2,
                    )
                    cost = 1000
                else:
                    weapon = Pistol(
                        self.player.rect.center,
                        name="Pistol+max",
                        max_ammo=25,
                        shot_cooldown=settings.PISTOL_COOLDOWN / 2,
                    )
                    cost = 5000
                success = self.tool_manager.purchase_weapon(self.player, weapon, cost)
                self.shop_message = (
                    f"{weapon.name} gekauft." if success
                    else "Nicht genug Coins oder kein Inventarplatz."
                )
            elif index in (4, 5, 6, 7):
                if index == 4:
                    from world.tools.healing import Healing

                    success = self.tool_manager.purchase_stackable_tool(
                        Healing((0, 0)), 150
                    )
                    name = "Healing"
                elif index == 5:
                    from world.tools.magic_powder import MagicPowder

                    success = self.tool_manager.purchase_stackable_tool(
                        MagicPowder((0, 0)), 400
                    )
                    name = "Magic Powder"
                elif index == 6:
                    success = self.tool_manager.purchase_energy()
                    name = "Energy"
                else:
                    from world.tools.smoke_bomb import SmokeBomb

                    success = self.tool_manager.purchase_stackable_tool(
                        SmokeBomb((0, 0)), 200
                    )
                    name = "Smoke Bomb"
                self.shop_message = (
                    f"{name} gekauft." if success
                    else "Nicht genug Coins, Inventarplatz oder Stack-Platz."
                )
            else:
                self.pause_page = "main"
                self.pause_menu_selected_index = 0
        elif self.pause_page == "levels":
            if index < len(self.LEVEL_OPTIONS):
                level_key, _ = self.LEVEL_OPTIONS[index]
                state_manager.replace(
                    Gameplay(
                        initial_money=self.tool_manager.money,
                        level=level_key,
                    )
                )
            else:
                self.pause_page = "main"
                self.pause_menu_selected_index = 0
        elif index == 0:
            audio.set_master_volume(audio.master_volume - 0.1)
        elif index == 1:
            audio.set_master_volume(audio.master_volume + 0.1)
        else:
            self.pause_page = "main"
            self.pause_menu_selected_index = 0

        self._layout_pause_buttons(pygame.display.get_surface().get_size())

    def _pause_labels(self):
        if self.pause_page == "shop":
            return (
                "Munition - 300 Coins",
                "Pistol - 400 Coins",
                "Pistol+ - 1000 Coins",
                "Pistol+max - 5000 Coins",
                "Healing - 150 Coins",
                "Magic Powder - 400 Coins",
                "Energy - 150 Coins",
                "Smoke Bomb - 200 Coins",
                "Back",
            )
        if self.pause_page == "levels":
            return tuple(label for _, label in self.LEVEL_OPTIONS) + ("Back",)
        if self.pause_page == "settings":
            return ("Volume -", "Volume +", "Back")
        return ("Resume", "Shop", "Settings", "Levels", "Restart Level")

    def _draw_pause_menu(self, screen):
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        title_text = {
            "main": "Pause",
            "shop": "Shop",
            "settings": "Settings",
            "levels": "Select Level",
        }[
            self.pause_page
        ]
        title = self.interaction_feedback_font.render(title_text, True, (255, 255, 255))
        screen.blit(title, title.get_rect(center=(screen.get_width() // 2, 120)))

        if self.pause_page == "shop":
            money = self.money_font.render(
                f"Coins: {self.tool_manager.money}", True, (255, 219, 88)
            )
            screen.blit(money, money.get_rect(center=(screen.get_width() // 2, 165)))
        elif self.pause_page == "settings":
            volume = self.money_font.render(
                f"Volume: {round(audio.master_volume * 100)}%",
                True,
                (255, 219, 88),
            )
            screen.blit(volume, volume.get_rect(center=(screen.get_width() // 2, 165)))

        for index, rect in enumerate(self.pause_buttons):
            selected = index == self.pause_menu_selected_index
            color = (230, 181, 76) if selected else (235, 235, 235)
            pygame.draw.rect(screen, (35, 40, 48, 220) if selected else (18, 22, 28, 220), rect, border_radius=6)
            pygame.draw.rect(screen, color, rect, 3 if selected else 1, border_radius=6)
            label = self.small_font.render(self._pause_labels()[index], True, color)
            screen.blit(label, label.get_rect(center=rect.center))
        if self.pause_page == "shop" and self.shop_message:
            message = self.interaction_feedback_font.render(
                self.shop_message, True, (255, 255, 255)
            )
            screen.blit(
                message,
                message.get_rect(
                    center=(screen.get_width() // 2, screen.get_height() - 55)
                ),
            )

    def _update_death_screen(self, events):
        screen = pygame.display.get_surface()
        self.continue_button = pygame.Rect(
            (screen.get_width() - 320) // 2,
            screen.get_height() // 2 + 60,
            320,
            60,
        )
        for event in events:
            if event.type == pygame.KEYDOWN and event.key in (
                pygame.K_RETURN,
                pygame.K_KP_ENTER,
                pygame.K_SPACE,
            ):
                self._continue_after_death()
            elif (
                event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
                and self.continue_button.collidepoint(event.pos)
            ):
                self._continue_after_death()

    def _continue_after_death(self):
        state_manager.replace(
            Gameplay(initial_money=self.tool_manager.money, level=self.level_name)
        )

    def _draw_death_screen(self, screen):
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 220))
        screen.blit(overlay, (0, 0))
        title = self.interaction_feedback_font.render(
            "You are dead", True, (255, 255, 255)
        )
        screen.blit(
            title,
            title.get_rect(
                center=(screen.get_width() // 2, screen.get_height() // 2 - 45)
            ),
        )
        pygame.draw.rect(screen, (35, 40, 48), self.continue_button, border_radius=6)
        pygame.draw.rect(
            screen, (230, 181, 76), self.continue_button, 2, border_radius=6
        )
        label = self.small_font.render("Continue", True, (255, 255, 255))
        screen.blit(label, label.get_rect(center=self.continue_button.center))

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
            "Press SPACE to continue", True, (255, 255, 255)
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
            if self.completion_elapsed >= (
                self.level_meta.COMPLETION_FADE_DURATION
                + self.level_meta.COMPLETION_MESSAGE_DURATION
            ):
                prompt = self.small_font.render(
                    "Press ENTER to replay this level", True, (255, 255, 255)
                )
                screen.blit(
                    prompt,
                    prompt.get_rect(
                        center=(screen.get_width() // 2, screen.get_height() // 2 + 100)
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
            lines.append("Press SPACE to continue.")

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
        if held_tool and held_tool.name.startswith("Pistol"):
            self.ammo_label.set_text(f"{held_tool.name}: {held_tool.amount} Schuss")
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

        