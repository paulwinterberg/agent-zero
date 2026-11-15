import os
import tempfile

import pygame

from moviepy import VideoFileClip
from core import renderer, state_manager
from states.gameplay import Gameplay
from states.game_state import GameState


class IntroVideo(GameState):
    def __init__(self):
        self.clip = VideoFileClip("assets/videos/intro.mp4")
        self.fps = self.clip.fps
        self.duration = self.clip.duration
        self.has_audio = self.clip.audio is not None
        self.audio_path = None

        if self.has_audio:
            # unique temp file, so it can't collide with another run or leftover file
            fd, self.audio_path = tempfile.mkstemp(suffix=".wav")
            os.close(fd)
            self.clip.audio.write_audiofile(self.audio_path, fps=44100, logger=None)
            pygame.mixer.music.load(self.audio_path)

        self.frames = self.clip.iter_frames(fps=self.fps, dtype="uint8")
        self.frame_idx = -1
        self.frame_surf = None
        self.video_done = False

        self.started = False
        self.elapsed = 0.0
        self.close_time = self.duration + 10

    def _cleanup(self):
        """Stop audio, release the file handle, and delete the temp WAV. Safe to call twice."""
        if self.has_audio:
            pygame.mixer.music.stop()
            try:
                pygame.mixer.music.unload()  # releases the file (required on Windows), pygame 2.0+
            except AttributeError:
                pass

        if self.audio_path:
            try:
                os.remove(self.audio_path)
            except OSError:
                pass  # already gone or still locked; not worth crashing over
            self.audio_path = None

        if self.clip is not None:
            self.clip.close()
            self.clip = None

    def _video_time(self):
        if self.has_audio:
            pos = pygame.mixer.music.get_pos()
            if pos >= 0:
                return pos / 1000.0
        return self.elapsed

    def _scale_to_screen(self, frame):
        surf = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
        tw, th = renderer.screen.get_size()
        vw, vh = surf.get_size()
        scale = min(tw / vw, th / vh)
        return pygame.transform.smoothscale(surf, (int(vw * scale), int(vh * scale)))

    def update(self, dt, events):
        if not self.started:
            self.started = True
            if self.has_audio:
                pygame.mixer.music.play()
            return

        self.elapsed += dt

        if self.elapsed >= self.close_time:
            self._cleanup()
            state_manager.replace(Gameplay(level="tutorial"))
            return

        if not self.video_done:
            target = int(self._video_time() * self.fps)
            last = None
            while self.frame_idx < target:
                try:
                    last = next(self.frames)
                except StopIteration:
                    self.video_done = True
                    break
                self.frame_idx += 1
            if last is not None:
                self.frame_surf = self._scale_to_screen(last)

            # video finished: audio has nothing left to play, so clean up early
            if self.video_done:
                self._cleanup()

    def draw(self, screen: pygame.Surface, dt):
        target = renderer.screen
        target.fill((0, 0, 0))

        if self.frame_surf is not None and not self.video_done:
            tw, th = target.get_size()
            sw, sh = self.frame_surf.get_size()
            target.blit(self.frame_surf, ((tw - sw) // 2, (th - sh) // 2))

        pygame.display.flip()