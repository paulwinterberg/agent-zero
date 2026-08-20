from abc import abstractmethod

import pygame

class State:   
    @abstractmethod
    def draw(self, screen: pygame.Surface, dt):
        pass
    
    @abstractmethod
    def update(self, dt: float, events: list):
        pass