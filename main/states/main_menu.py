import pygame

from states.state import State


class MainMenu(State):
    def __init__(self):
        self.title_image = pygame.image.load("assets/ui/title_screen.png")
        self.screen_size = pygame.display.get_desktop_sizes()[0]
        
        self.playFont = pygame.font.Font("assets/fonts/PixelifySans-Medium.ttf", 35)
        self.playText = self.playFont.render("PRESS [F]", True, (255, 255, 255))
        self.playTextRect = self.playText.get_rect(center=(self.screen_size[0]/2, self.screen_size[1] - 100))
        
        self.title_image = pygame.transform.scale(self.title_image, self.screen_size)
        
        self.alpha = 0.0
        self.fade_speed = 255 / 1.5
        self.title_image.set_alpha(0)
        
        self.accumulated = 0
        self.loaded_music = False
        
        #pygame.mixer.music.load("assets\\music\\intro_music.mp3")
        #pygame.mixer.music.set_volume(1.0)
    
    def update(self, dt, events):
        self.accumulated += dt
        if self.accumulated < 3: return
        
        if not self.loaded_music:
            #pygame.mixer.music.play(loops=-1)
            self.loaded_music = True
            
        if self.accumulated < 3.5: return
        
        if self.alpha < 255:
            self.alpha = min(255, self.alpha + self.fade_speed * dt)
            self.title_image.set_alpha(int(self.alpha))
    
    def draw(self, screen: pygame.Surface, dt):
        screen.fill((0, 0, 0))
        screen.blit(self.title_image, (0, 0))
        
        if self.accumulated > 10:
            screen.blit(self.playText, self.playTextRect)