from world.tilemap import TileMap
from entities.enemy import Enemy

class EnemyManager:
    def __init__(self, tilemap: TileMap, group=None):
        self.tilemap = tilemap
        self.group = group
        self.enemy_spawns = []
        self.enemies = []
        
        self._load_enemy_spawns()
        self._load_enemies()

    def _load_enemy_spawns(self):
        for spawn in self.tilemap.get_spawns():
            if spawn["type"] == "EnemySpawn":
                self.enemy_spawns.append(spawn)
                
    def _load_enemies(self):
        for spawn in self.enemy_spawns:
            path = self.get_enemy_path(spawn["name"])


            enemy = Enemy((spawn["rect"].left, spawn["rect"].top), path)
            self.enemies.append(enemy)

            if self.group is not None:
                self.group.add(enemy, layer=self.tilemap.y_sort_layer(enemy.rect.bottom))

    def get_enemy_path(self, enemy_name):
        prefix = enemy_name + "_"
        path_index = 1
        path_markers = []

        while True:
            marker = self.tilemap.get_object("Paths", prefix+str(path_index))
            if not marker:
                break

            path_markers.append(marker)
            path_index += 1

        return path_markers if len(path_markers) > 0 else None
    
    def update(self, dt):
        for enemy in self.enemies:
            enemy.update(dt)
            if self.group is not None:
                self.group.change_layer(enemy, self.tilemap.y_sort_layer(enemy.rect.bottom))