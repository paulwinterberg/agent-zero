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
            enemy = Enemy((spawn["rect"].left, spawn["rect"].top))
            self.enemies.append(enemy)

            if self.group is not None:
                self.group.add(enemy, layer=self.tilemap.y_sort_layer(enemy.rect.bottom))
    
    def update(self, dt):
        for enemy in self.enemies:
            enemy.update(dt)
            if self.group is not None:
                self.group.change_layer(enemy, self.tilemap.y_sort_layer(enemy.rect.bottom))