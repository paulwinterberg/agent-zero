from world.tilemap import TileMap
from entities.enemy import Enemy
from entities.boss import BossEnemy
from entities.scientist import Scientist
from globals import globs

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

        self._assign_enemy_groups()
        if self.boss is not None:
            self.boss.enemy_manager = self
        globs["agent_x"] = self.boss

    def _assign_enemy_groups(self):
        groups = {}
        for enemy in self.enemies:
            group_id = enemy.groupId
            if not group_id:
                continue

            groups.setdefault(group_id, []).append(enemy)

        for group in groups.values():
            for enemy in group:
                enemy.set_group(group)

    def respawn_map_enemies(self):
        for enemy in tuple(self.enemies):
            if enemy is self.boss:
                continue
            self._remove_enemy(enemy)

        self.enemies = [self.boss] if self.boss is not None else []
        for spawn in self.enemy_spawns:
            if spawn["type"] != "EnemySpawn":
                continue
            enemy = Enemy(
                (spawn["rect"].left, spawn["rect"].top),
                self.get_enemy_path(spawn["name"]),
                tool_manager=self.tool_manager,
                groupId=spawn["properties"].get("EnemyGroup"),
            )
            self._add_enemy(enemy)

        map_enemies = [enemy for enemy in self.enemies if enemy is not self.boss]
        for index, enemy in enumerate(map_enemies):
            offset = 36 if index % 2 == 0 else -36
            extra_enemy = Enemy(
                (enemy.rect.centerx + offset, enemy.rect.centery),
                tool_manager=self.tool_manager,
            )
            self._add_enemy(extra_enemy)

        self._assign_enemy_groups()

    def _remove_enemy(self, enemy):
        enemy.kill()
        tool = enemy.tool
        if tool is not None and tool not in self.tool_manager.inventory:
            if tool.held_sprite is not None:
                tool.held_sprite.kill()
            tool.sprite.kill()
            if tool in self.tool_manager.tools:
                self.tool_manager.tools.remove(tool)

        for sprite in self.tool_manager.sprite_group.sprites():
            projectile = getattr(sprite, "projectile", None)
            if getattr(projectile, "owner", None) is enemy:
                sprite.kill()

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