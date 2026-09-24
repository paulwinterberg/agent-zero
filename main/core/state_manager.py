import pygame
import core.renderer as renderer

from states.game_state import GameState

stack: list[GameState] = []

def push(state):
    stack.append(state)

def pop():
    stack.pop()

def update(dt, events):
    stack[-1].update(dt, events)

def get_state():
    return stack[-1]

def draw(screen, dt):
    for state in stack:
        state.draw(screen, dt)
    renderer.render_ui()
    pygame.display.flip()