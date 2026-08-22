import pygame

from settings import MUSIC_PATH, SFX_PATH

loaded_files = {}

def play_sound(path: str, loops: int = 0, fade_ms: int = 0, volume: float = 1.0) -> pygame.mixer.Sound:
    loaded: pygame.mixer.Sound = loaded_files.get(path) or load_sound(path)
    loaded.play(loops=loops, fade_ms=fade_ms)
    loaded.set_volume(volume)
    return loaded
    
def play_sfx(name: str, loops: int = 0, fade_ms: int = 0, volume: float = 1.0) -> pygame.mixer.Sound:
    return play_sound(SFX_PATH+"/"+name, loops, fade_ms, volume)

def play_music(name: str, loops: int = 0, fade_ms: int = 0, volume: float = 1.0) -> pygame.mixer.music:
    pygame.mixer.music.load(MUSIC_PATH+"/"+name)
    pygame.mixer.music.set_volume(volume)
    pygame.mixer.music.play(loops=loops, fade_ms=fade_ms)
    
    return pygame.mixer.music

def stop_music(fade_ms:int =0):
    pygame.mixer.music.fadeout(fade_ms)
   
def load_sound(path: str):
    sound = pygame.mixer.Sound(path)
    loaded_files[path] = sound
    
    return sound

def is_loaded(path: str):
    return loaded_files[path] != None