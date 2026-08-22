import pygame

from core import game, audio, screen
from states.gameplay import Gameplay
from states.state import State


class MainMenu(State):
    def __init__(self):
        self.title_image = pygame.image.load("assets/ui/title_screen.png")
        self.screen_size = screen.get_screen_size()
        
        self.playFont = pygame.font.Font("assets/fonts/PixelifySans-Medium.ttf", 35)
        self.playText = self.playFont.render("PRESS [F]", True, (255, 255, 255))
        self.playTextRect = self.playText.get_rect(center=(self.screen_size.x / 2, self.screen_size.y - 100))
        
        self.title_image = pygame.transform.scale(self.title_image, self.screen_size)
        
        self.alpha = 0.0
        self.fade_speed = 255 / 1.5
        self.title_image.set_alpha(0)
        
        self.accumulated = 0
        self.loaded_music = False
        self.accumulatedSinceFadeoutStart = 0
        
        self.fadeOut = False
    
    def update(self, dt, events):
        self.accumulated += dt
        if self.accumulated < 3: return
        
        if not self.loaded_music:
            audio.play_music("intro_music.mp3")
            self.loaded_music = True
            
        if self.accumulated < 3.5: return
        
        if self.alpha < 255 and not self.fadeOut:
            self.alpha = min(255, self.alpha + self.fade_speed * dt)
            self.title_image.set_alpha(int(self.alpha))
        
        if self.accumulated < 10: return
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_f] and not self.fadeOut:
            self.fadeOut = True
            audio.play_sfx("button_click.mp3")
            
        if not self.fadeOut: return
        
        self.accumulatedSinceFadeoutStart += dt
        
        if self.accumulatedSinceFadeoutStart < 1: return
        
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.fadeout(1000)
        
        if self.alpha > 0:
            self.alpha = max(0, self.alpha - self.fade_speed * dt)
            self.title_image.set_alpha(int(self.alpha))
            
        if self.alpha == 0 and self.accumulatedSinceFadeoutStart > 5:
            game.state_manager.pop()
            game.state_manager.push(Gameplay())
    
    def draw(self, screen: pygame.Surface, dt):
        screen.fill((0, 0, 0))
        screen.blit(self.title_image, (0, 0))
        
        if self.accumulated > 10 and not self.fadeOut:
            screen.blit(self.playText, self.playTextRect)