# Explains how to code stuff

## Audio
Lets you load, play, and control audio. <br> 
```py
from core import audio
```
```py
#to play a sound effect or music:
track = audio.<play_sfx/play_music>(
    name="filename.mp3", 
    loops=NUM_LOOPS, 
    fade_ms=FADE_IN_TIME,
    volume=VOLUME
)
```

```py
#to control the track:
track.stop() #immediately stops the track
track.fadeout(FADE_OUT_TIME) #gradually fades out the track
track.set_volume(VOLUME) #updates the volume of the track
```

```py
#if you want to load a file without playing:
track = audio.load_sound(path="path/to/file.mp3")
```

```py
#if you want to play a sound outside of assets/sfx and assets/music:
track = audio.play_sound(
    path="path/to/file.mp3", 
    loops=NUM_LOOPS, 
    fade_ms=FADE_IN_TIME,
    volume=VOLUME
)
```

## Screen
Lets you control and get info about the screen.
```py
from core import screen
```
```py
#to get the screen size
screen_size: Vector2 = screen.get_screen_size()
```
```py
#to get the screen center
screen_center: Vector2 = screen.get_screen_center()
```
```py
#to update the window title
screen.set_caption(caption="New Caption")
```

## State Manager
Lets you load and unload states.
```py
from core.game import state_manager
```
```py
#to load a state
state_manager.push(STATE_OBJECT)

#for example
state_manager.push(Gamplay())
```
```py
#to unload the last state
state_manager.pop()
```

## States
States represent different "states" in the game. For example, the main menu is a state and gameplay is a state. This makes it very easy to organize code.
```py
from states.state import State

#to create a state
class STATE_NAME(State):

    def __init__(self):
        #runs when the state is created
        pass

    def update(self, dt: float, events: list):
        #runs every frame BEFORE rendering
        pass

    def draw(self, screen: pygame.Surface, dt: float):
        #runs every frame to render 
        pass
```

## Renderer & Tilemaps
How to load tilemaps and render them
```py
from core.game import renderer
from world.tilemap import TileMap
from entities.player import Player
from pyscroll import PyscrollGroup
```
```py
#a player is required to load a tilemap
player = Player(pos=(x, y))
```
```py
#to load a tilemap
tilemap: TileMap, group: PyscrollGroup = renderer.load_tilemap(
    path="path/to/map.tmx", 
    player=player
)
```
```py
#to render a tilemap
renderer.render_world(
    dt=DELTA_TIME, 
    tilemap=tilemap, 
    group=group, 
    player=player
)
```
# Creating Tilemaps
## Basic Setup:
Layers:
-    Spawns (Object)
-    Interactions (Object)
-    Collisions (Object)
-    Objects (Object)
-    Any tile layers for the ground

## Custom Properties
**1. BottomOffset <br>**
If there's an object where the actual bottom of the object is higher than the bottom of the tile, this will lead to issues with the player always being behind the object. To fix this,
add the BottomOffset property as an `int` and set it to the amount of pixels that the bottom should be moved _up_ by.
