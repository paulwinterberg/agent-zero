from settings import ENEMY_VISION_RADIUS #pixels

class Perception:
    def __init__(self, enemy, player):
        self.enemy = enemy
        self.player = player

    def can_see_player(self) -> bool:
        pass