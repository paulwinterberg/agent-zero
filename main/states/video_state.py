import os
import tempfile

import pygame
from moviepy import VideoFileClip

from core import renderer
from states.game_state import GameState


class VideoState(GameState):
    """
    Base state that plays a video file, synced to its audio track.

    Args:
        path:            Path to the video file.
        hold_time:       Seconds to stay on this state after the video ends.
        hold_last_frame: Keep the last frame on screen during hold_time
                         (otherwise the screen goes black).
        start_delay:     Seconds of black screen before playback begins.

    Subclasses typically override:
        on_start()      - called once when the delay is over and playback begins
        on_video_end()  - called once, as soon as the last frame has been decoded
        on_finished()   - called once, `hold_time` seconds after the video ends
    """

    def __init__(self, path: str, hold_time: float = 0.0, hold_last_frame: bool = False,
                 start_delay: float = 0.0):
        self.clip = VideoFileClip(path)
        self.fps = self.clip.fps
        self.duration = self.clip.duration
        self.has_audio = self.clip.audio is not None
        self.audio_path = None

        self.start_delay = start_delay
        self.hold_last_frame = hold_last_frame
        self.end_time = self.duration + hold_time

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
        self.finished = False

        self.started = False
        self.delay_elapsed = 0.0   # time spent waiting before playback
        self.elapsed = 0.0         # time since playback began

    # ------------------------------------------------------------------ hooks

    def on_start(self):
        """Called once, when the start delay is over and playback begins."""

    def on_video_end(self):
        """Called once when the last frame has been decoded."""

    def on_finished(self):
        """Called once when elapsed time reaches duration + hold_time."""

    # --------------------------------------------------------------- internals

    def close(self):
        """Stop audio, release the file handle, delete the temp WAV. Safe to call twice."""
        if self.has_audio:
            pygame.mixer.music.stop()
            try:
                pygame.mixer.music.unload()  # releases the file (required on Windows), pygame 2.0+
            except AttributeError:
                pass
            self.has_audio = False

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

    def _advance_frames(self):
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

        if self.video_done:
            # audio has nothing left to play, so clean up early
            self.close()
            self.on_video_end()

    # ---------------------------------------------------------- GameState API

    def update(self, dt, events):
        if self.finished:
            return

        if not self.started:
            self.delay_elapsed += dt
            if self.delay_elapsed >= self.start_delay:
                self.started = True
                if self.has_audio:
                    pygame.mixer.music.play()
                self.on_start()
            return

        self.elapsed += dt

        if self.elapsed >= self.end_time:
            self.finished = True
            self.close()
            self.on_finished()
            return

        if not self.video_done:
            self._advance_frames()

    def draw(self, screen: pygame.Surface, dt):
        target = renderer.screen
        target.fill((0, 0, 0))

        show = self.frame_surf is not None and (not self.video_done or self.hold_last_frame)
        if show:
            tw, th = target.get_size()
            sw, sh = self.frame_surf.get_size()
            target.blit(self.frame_surf, ((tw - sw) // 2, (th - sh) // 2))

        pygame.display.flip()