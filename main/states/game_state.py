from abc import abstractmethod

import pygame

class GameState:   
    @abstractmethod
    def draw(self, screen: pygame.Surface, dt: float):
        pass
    
    @abstractmethod
    def update(self, dt: float, events: list):
        pass