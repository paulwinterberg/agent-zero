import os
import pygame

from settings import MUSIC_PATH, SFX_PATH

loaded_files = {}
_mixer_ready = False


def init_audio():
    """Initialize the mixer, falling back to a dummy driver if no audio device is available."""
    global _mixer_ready
    if _mixer_ready:
        return

    try:
        pygame.mixer.init()
        _mixer_ready = True
    except pygame.error:
        # No real audio device (e.g. noVNC / headless) — use SDL's dummy driver instead
        os.environ["SDL_AUDIODRIVER"] = "dummy"
        try:
            pygame.mixer.quit()
        except pygame.error:
            pass
        pygame.mixer.init()
        _mixer_ready = True


def play_sound(path: str, loops: int = 0, fade_ms: int = 0, volume: float = 1.0) -> pygame.mixer.Sound:
    init_audio()
    loaded: pygame.mixer.Sound = loaded_files.get(path) or load_sound(path)
    loaded.set_volume(volume)
    loaded.play(loops=loops, fade_ms=fade_ms)
    return loaded


def play_sfx(name: str, loops: int = 0, fade_ms: int = 0, volume: float = 1.0) -> pygame.mixer.Sound:
    return play_sound(SFX_PATH + "/" + name, loops, fade_ms, volume)


def play_music(name: str, loops: int = 0, fade_ms: int = 0, volume: float = 1.0) -> pygame.mixer.music:
    init_audio()
    pygame.mixer.music.load(MUSIC_PATH + "/" + name)
    pygame.mixer.music.set_volume(volume)
    pygame.mixer.music.play(loops=loops, fade_ms=fade_ms)
    return pygame.mixer.music


def stop_music(fade_ms: int = 0):
    pygame.mixer.music.fadeout(fade_ms)


def load_sound(path: str):
    sound = pygame.mixer.Sound(path)
    loaded_files[path] = sound
    return sound


def is_loaded(path: str):
    return loaded_files.get(path) is not None