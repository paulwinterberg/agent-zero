import pygame

from moviepy import VideoFileClip
from core import renderer, state_manager
from states.gameplay import Gameplay
from states.game_state import GameState

class IntroVideo(GameState):
    def __init__(self, video_path="assets/videos/intro.mp4", on_complete=None):
        self.clip = VideoFileClip(video_path)
        self.on_complete = on_complete
        if self.clip.audio:
            self.clip.audio.write_audiofile("temp_audio.wav")  # wav = no decode lag at startup
            pygame.mixer.music.load("temp_audio.wav")
            pygame.mixer.music.play()
            
        self.elapsed = 0
        self.close_time = self.clip.duration + (10 if on_complete is None else 0)

    def update(self, dt, events):
        self.elapsed += dt
        if self.elapsed >= self.close_time:
            self.clip.close()
            self.clip = None
            if self.on_complete is not None:
                on_complete = self.on_complete
                state_manager.pop()
                on_complete()
            else:
                state_manager.replace(Gameplay(level="tutorial"))

    def exit(self):
        if self.clip is not None:
            self.clip.close()
            self.clip = None
        pygame.mixer.music.stop()

    def draw(self, screen: pygame.Surface, dt):
        if self.elapsed > self.clip.duration:
            renderer.screen.fill((0, 0, 0, 0))
            return pygame.display.flip()
        
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