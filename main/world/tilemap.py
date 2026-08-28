import pygame
import pyscroll
import pytmx


class TileMap:
    def __init__(self, filename, zoom_level=1.0):
        tmx_data = pytmx.util_pygame.load_pygame(filename)
        self.tmx_data = tmx_data
        self.width = tmx_data.width * tmx_data.tilewidth
        self.height = tmx_data.height * tmx_data.tileheight

        # Walls becomes a set of sortable sprites, not a static
        # background tile layer — hide it from pyscroll's own
        # rendering pass so it isn't drawn twice.
        walls_layer = tmx_data.get_layer_by_name("Walls")
        walls_layer.visible = False

        # Everything at/above this fractional layer gets y-sorted;
        # Decorations + Floor stay fixed static layers below it.
        self.sort_base_layer = self.get_layer_index("Decorations") + 1

        self.collision_rects = self._load_collisions()
        self.walls = self._load_tile_layer_as_sprites("Walls")
        self.decorations = self._load_tile_layer_as_sprites("Decorations2")

        map_data = pyscroll.data.TiledMapData(tmx_data)
        self.map_layer = pyscroll.orthographic.BufferedRenderer(
            map_data,
            pygame.display.get_desktop_sizes()[0]
        )
        self.map_layer.zoom = zoom_level

    def y_sort_layer(self, pixel_y):
        """Fractional pyscroll layer, monotonic in pixel_y, always
        above the static Decorations/Floor layers. Used for the
        player, Walls-as-sprites and Decorations2-as-sprites alike,
        so they all sort against each other purely by depth."""
        return self.sort_base_layer + (pixel_y / self.tmx_data.tileheight)

    def zoom_to(self, zoom_level):
        self.map_layer.zoom = zoom_level

    def get_object(self, layer_name, object_name) -> pytmx.TiledObject | None:
        try:
            layer = self.tmx_data.get_layer_by_name(layer_name)
        except ValueError:
            return None
        if not isinstance(layer, pytmx.TiledObjectGroup):
            return None
        for obj in layer:
            if obj.name == object_name:
                return obj
        return None

    def get_layer_index(self, layer_name):
        for i, layer in enumerate(self.tmx_data.visible_layers):
            if layer.name == layer_name:
                return i
        return None

    def _load_collisions(self):
        rects = []

        # Iterate ALL layers, not just visible_layers — Walls is
        # intentionally hidden now, but its colliders still matter.
        for layer in self.tmx_data.layers:
            if not isinstance(layer, pytmx.TiledTileLayer):
                continue
            for x, y, gid in layer:
                if gid == 0:
                    continue
                props = self.tmx_data.get_tile_properties_by_gid(gid)
                if not props or not props.get("colliders"):
                    continue
                tile_world_x = x * self.tmx_data.tilewidth
                tile_world_y = y * self.tmx_data.tileheight
                for collider in props["colliders"]:
                    rects.append(pygame.Rect(
                        tile_world_x + collider.x,
                        tile_world_y + collider.y,
                        collider.width,
                        collider.height
                    ))

        try:
            collision_layer = self.tmx_data.get_layer_by_name("Collisions")
        except ValueError:
            collision_layer = None

        if isinstance(collision_layer, pytmx.TiledObjectGroup):
            for obj in collision_layer:
                rects.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))

        return rects

    def _find_tile_clusters(self, layer):
        """Group orthogonally-connected non-empty cells into clusters,
        so a multi-tile object sorts as one unit off its lowest row.
        Caveat: two separate objects placed touching each other will
        merge into one cluster — leave a gap between them in Tiled,
        or extend this with per-tile 'object_id' properties if you
        need adjacent objects to stay independent."""
        cells = {}
        for x, y, gid in layer:
            if gid != 0:
                cells[(x, y)] = gid

        visited = set()
        clusters = []
        for start in cells:
            if start in visited:
                continue
            stack = [start]
            visited.add(start)
            cluster = []
            while stack:
                cx, cy = stack.pop()
                cluster.append((cx, cy, cells[(cx, cy)]))
                for nx, ny in ((cx+1, cy), (cx-1, cy), (cx, cy+1), (cx, cy-1)):
                    if (nx, ny) in cells and (nx, ny) not in visited:
                        visited.add((nx, ny))
                        stack.append((nx, ny))
            clusters.append(cluster)
        return clusters

    def _load_tile_layer_as_sprites(self, layer_name):
        sprites = []
        layer = self.tmx_data.get_layer_by_name(layer_name)

        for cluster in self._find_tile_clusters(layer):
            base_row = max(y for x, y, gid in cluster)
            base_bottom_y = (base_row + 1) * self.tmx_data.tileheight
            sort_layer = self.y_sort_layer(base_bottom_y)

            for x, y, gid in cluster:
                image = self.tmx_data.get_tile_image_by_gid(gid)
                if not image:
                    continue
                pos = (x * self.tmx_data.tilewidth, y * self.tmx_data.tileheight)
                sprites.append(Decoration(image, pos, sort_layer))

        return sprites


class Decoration(pygame.sprite.Sprite):
    def __init__(self, image, pos, layer=0):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(topleft=pos)
        self._layer = layer