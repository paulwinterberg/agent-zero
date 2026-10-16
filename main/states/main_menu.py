import pygame

from core import audio, game
from states.gameplay import Gameplay
from states.game_state import GameState

CURRENT_LEVEL = "tutorial"

class MainMenu(GameState):
    MENU_ITEMS = ("Play", "Settings")

    def __init__(self, money=0):
        self.title_image = pygame.image.load("assets/ui/title_screen.png").convert()
        self.background_size = pygame.display.get_surface().get_size()
        self.background = pygame.transform.scale(self.title_image, self.background_size)
        self.font = pygame.font.Font("assets/fonts/PixelifySans-Medium.ttf", 38)
        self.small_font = pygame.font.Font("assets/fonts/PixelifySans-Medium.ttf", 26)
        self.money_font = pygame.font.Font("assets/fonts/PixelifySans-Medium.ttf", 26)
        self.money = money
        self.selected_item = 0
        self.page = "main"
        self.button_rects = []
        self.back_rect = pygame.Rect(0, 0, 0, 0)
        audio.play_music("intro_music.mp3")

    def update(self, dt, events):
        screen = pygame.display.get_surface()
        if screen is None:
            return

        self._layout_buttons(screen.get_size())
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w):
                    if self.page == "main":
                        self.selected_item = (self.selected_item - 1) % len(self.MENU_ITEMS)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    if self.page == "main":
                        self.selected_item = (self.selected_item + 1) % len(self.MENU_ITEMS)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    if self.page == "main":
                        self._activate_item(self.selected_item)
                    else:
                        self.page = "main"
                elif event.key == pygame.K_ESCAPE:
                    self.page = "main"
            elif event.type == pygame.MOUSEMOTION and self.page == "main":
                for index, rect in enumerate(self.button_rects):
                    if rect.collidepoint(event.pos):
                        self.selected_item = index
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.page == "main":
                    for index, rect in enumerate(self.button_rects):
                        if rect.collidepoint(event.pos):
                            self.selected_item = index
                            self._activate_item(index)
                            break
                elif self.back_rect.collidepoint(event.pos):
                    self.page = "main"

    def draw(self, screen: pygame.Surface, dt):
        if self.background_size != screen.get_size():
            self.background_size = screen.get_size()
            self.background = pygame.transform.scale(self.title_image, self.background_size)
        screen.blit(self.background, (0, 0))
        wallet = self.money_font.render(f"$ {self.money}", True, (255, 219, 88))
        screen.blit(
            wallet,
            wallet.get_rect(topright=(screen.get_width() - 28, 24)),
        )

        if self.page == "main":
            self._draw_main_menu(screen)
        else:
            self._draw_placeholder(screen)

    def _layout_buttons(self, screen_size):
        width, height = screen_size
        button_width = min(330, width - 48)
        button_height = 62
        x = 36
        first_y = max(110, height // 2 - 100)
        self.button_rects = [
            pygame.Rect(x, first_y + index * 78, button_width, button_height)
            for index in range(len(self.MENU_ITEMS))
        ]
        self.back_rect = pygame.Rect(x, height // 2 + 75, button_width, button_height)

    def _draw_main_menu(self, screen):
        title = self.font.render("Agent Zero", True, (255, 255, 255))
        screen.blit(title, (36, max(36, screen.get_height() // 2 - 190)))
        for index, (label, rect) in enumerate(zip(self.MENU_ITEMS, self.button_rects)):
            selected = index == self.selected_item
            color = (230, 181, 76) if selected else (235, 235, 235)
            pygame.draw.rect(
                screen,
                (35, 40, 48, 235) if selected else (18, 22, 28, 220),
                rect,
                border_radius=6,
            )
            pygame.draw.rect(
                screen,
                color,
                rect,
                3 if selected else 1,
                border_radius=6,
            )
            text = self.small_font.render(label, True, color)
            screen.blit(text, text.get_rect(center=rect.center))

    def _draw_placeholder(self, screen):
        label = "Coming soon."
        text = self.small_font.render(label, True, (255, 255, 255))
        screen.blit(text, text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 20)))
        pygame.draw.rect(
            screen,
            (35, 40, 48),
            self.back_rect,
            border_radius=6,
        )
        pygame.draw.rect(screen, (230, 181, 76), self.back_rect, 2, border_radius=6)
        back_text = self.small_font.render("Back", True, (255, 255, 255))
        screen.blit(back_text, back_text.get_rect(center=self.back_rect.center))

    def _activate_item(self, index):
        if index == 0:
            audio.stop_music(fade_ms=500)
            game.state_manager.replace(Gameplay(initial_money=self.money, level=CURRENT_LEVEL))
        elif index == 1:
            self.page = "settings"
