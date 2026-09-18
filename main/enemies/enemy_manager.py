from world.tilemap import TileMap

class EnemyManager:
    def __init__(self, tilemap: TileMap):
        self.tilemap = tilemap
        self.walls = []

    def _load_walls(self):
        pass