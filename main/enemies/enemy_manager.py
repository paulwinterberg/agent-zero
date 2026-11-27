from world.tilemap import TileMap
from entities.enemy import Enemy
from entities.boss import BossEnemy
from entities.scientist import Scientist

class EnemyManager:
    def __init__(self, tilemap: TileMap, group=None, tool_manager=None):
        self.tilemap = tilemap
        self.group = group
        self.tool_manager = tool_manager
        self.enemy_spawns = []
        self.enemies = []
        self.boss = None
        self.characters = []
        
        self._load_enemy_spawns()
        self._load_enemies()
        self._load_characters()

    def _load_enemy_spawns(self):
        for spawn in self.tilemap.get_spawns():
            if spawn["type"] in ("EnemySpawn", "BossSpawn"):
                self.enemy_spawns.append(spawn)
                
    def _load_enemies(self):
        for spawn in self.enemy_spawns:
            if spawn["type"] == "BossSpawn":
                enemy = BossEnemy(
                    (spawn["rect"].left, spawn["rect"].top),
                    tool_manager=self.tool_manager,
                    spawn_minions=self._spawn_boss_minions,
                )
                self.boss = enemy
            else:
                path = self.get_enemy_path(spawn["name"])
                enemy = Enemy(
                    (spawn["rect"].left, spawn["rect"].top),
                    path,
                    tool_manager=self.tool_manager,
                    groupId=spawn["properties"].get("EnemyGroup", None)
                )
            self._add_enemy(enemy)

        groups = {}
        for enemy in self.enemies:
            groupId = enemy.groupId
            if not groupId: continue

            if groupId in groups:
                groups[groupId].append(enemy)
            else:
                groups[groupId] = [enemy]

        for group in groups.values():
            for enemy in group:
                enemy.set_group(group)

    def _add_enemy(self, enemy):
        self.enemies.append(enemy)
        if self.group is not None:
            self.group.add(enemy, layer=self.tilemap.y_sort_layer(enemy.rect.bottom))

    def _spawn_boss_minions(self, boss):
        y = boss.rect.centery
        for x in (boss.rect.left - 20, boss.rect.right + 20):
            enemy = Enemy(
                (x, y),
                tool_manager=self.tool_manager,
            )
            self._add_enemy(enemy)

    def _load_characters(self):
        for spawn in self.tilemap.get_spawns():
            if spawn["type"] != "ScientistSpawn":
                continue
            scientist = Scientist(spawn["rect"].center, self.tilemap)
            self.characters.append(scientist)
            if self.group is not None:
                self.group.add(
                    scientist,
                    layer=self.tilemap.y_sort_layer(scientist.rect.bottom),
                )

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
        for enemy in tuple(self.enemies):
            enemy.update(dt)
            if self.group is not None:
                self.group.change_layer(enemy, self.tilemap.y_sort_layer(enemy.rect.bottom))
        for scientist in self.characters:
            scientist.update(dt)
            if self.group is not None:
                self.group.change_layer(
                    scientist,
                    self.tilemap.y_sort_layer(scientist.rect.bottom),
                )