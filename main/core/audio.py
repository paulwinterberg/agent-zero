import os
from os import path
import pygame

from settings import MUSIC_PATH, SFX_PATH

loaded_files = {}
_sound_volumes = {}
_mixer_ready = False
master_volume = 1.0
_music_volume = 1.0


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
    _sound_volumes[path] = volume
    loaded.set_volume(volume * master_volume)
    loaded.play(loops=loops, fade_ms=fade_ms)
    return loaded


def play_sfx(name: str, loops: int = 0, fade_ms: int = 0, volume: float = 1.0) -> pygame.mixer.Sound:
    return play_sound(SFX_PATH + "/" + name, loops, fade_ms, volume)


def play_music(name: str, loops: int = 0, fade_ms: int = 0, volume: float = 1.0) -> pygame.mixer.music:
    global _music_volume
    init_audio()
    pygame.mixer.music.load(MUSIC_PATH + "/" + name)
    _music_volume = volume
    pygame.mixer.music.set_volume(volume * master_volume)
    pygame.mixer.music.play(loops=loops, fade_ms=fade_ms)
    return pygame.mixer.music


def stop_music(fade_ms: int = 0):
    pygame.mixer.music.fadeout(fade_ms)

def load_sfx(name: str):
    return load_sound(SFX_PATH + "/" + name)

def load_sound(path: str):
    if path not in loaded_files:
        loaded_files[path] = pygame.mixer.Sound(path)
        _sound_volumes[path] = 1.0
    return loaded_files[path]


def set_master_volume(volume: float):
    global master_volume
    master_volume = max(0.0, min(1.0, volume))
    pygame.mixer.music.set_volume(_music_volume * master_volume)
    for path, sound in loaded_files.items():
        sound.set_volume(_sound_volumes[path] * master_volume)


def is_loaded(path: str):
    return loaded_files.get(path) is not None