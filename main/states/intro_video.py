import pygame

from moviepy import VideoFileClip
from core import renderer, state_manager
from states.gameplay import Gameplay
from states.game_state import GameState

class IntroVideo(GameState):
    def __init__(self):
        self.clip = VideoFileClip("assets/videos/intro.mp4")
        if self.clip.audio:
            self.clip.audio.write_audiofile("temp_audio.wav")  # wav = no decode lag at startup
            pygame.mixer.music.load("temp_audio.wav")
            pygame.mixer.music.play()
            
        self.elapsed = 0

    def update(self, dt, events):
        self.elapsed += dt
        if self.elapsed >= self.clip.duration:
            state_manager.replace(Gameplay(level="tutorial"))

    def draw(self, screen: pygame.Surface, dt):
        t = min(self.elapsed, self.clip.duration - 0.001)
        frame = self.clip.get_frame(t)
        surf = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
    
        target = renderer.screen
        tw, th = target.get_size()
        vw, vh = surf.get_size()
        scale = min(tw / vw, th / vh)
        new_size = (int(vw * scale), int(vh * scale))
    
        surf = pygame.transform.smoothscale(surf, new_size)
        target.fill((0, 0, 0))
        target.blit(surf, ((tw - new_size[0]) // 2, (th - new_size[1]) // 2))
        pygame.display.flip()