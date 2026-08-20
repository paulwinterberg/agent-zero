import pygame

from states.state import State

class StateManager:
    def __init__(self):
        self.stack: list[State] = []

    def push(self, state):
        self.stack.append(state)

    def pop(self):
        self.stack.pop()

    def update(self, dt, events):
        self.stack[-1].update(dt, events)

    def draw(self, screen, dt):
        for state in self.stack:
            state.draw(screen, dt)
            
        pygame.display.flip()