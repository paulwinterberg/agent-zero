import pygame
import pyscroll
import pytmx

class TileMap:
    def __init__(self, filename, zoom_level=1.0):
        tmx_data = pytmx.util_pygame.load_pygame(filename)
        self.tmx_data = tmx_data
        self.width = tmx_data.width * tmx_data.tilewidth
        self.height = tmx_data.height * tmx_data.tileheight
        self.collision_rects = self._load_collisions()
        self.decorations = self._load_decorations()

        map_data = pyscroll.data.TiledMapData(tmx_data)
        self.map_layer = pyscroll.orthographic.BufferedRenderer(
            map_data,
            pygame.display.get_desktop_sizes()[0]
        )
        self.map_layer.zoom = zoom_level
        
    def zoom_to(self, zoom_level):
        self.map_layer.zoom = zoom_level
        
    def get_object(self, layer_name, object_name)-> pytmx.TiledObject | None:
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

        # individual tiles hitboxes
        for layer in self.tmx_data.visible_layers:
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

        # object layer called collisions
        try:
            collision_layer = self.tmx_data.get_layer_by_name("Collisions")
        except ValueError:
            collision_layer = None

        if isinstance(collision_layer, pytmx.TiledObjectGroup):
            for obj in collision_layer:
                rects.append(pygame.Rect(
                    obj.x, obj.y, obj.width, obj.height
                ))

        return rects

    def _load_decorations(self):
        decorations = []
        layer = self.tmx_data.get_layer_by_name("Decorations")
        layer_index = self.get_layer_index("Decorations")
        for x, y, gid in layer:
            if gid == 0:
                continue
            image = self.tmx_data.get_tile_image_by_gid(gid)
            if image:
                pos = (x * self.tmx_data.tilewidth, y * self.tmx_data.tileheight)
                decorations.append(Decoration(image, pos, layer_index))
        return decorations
    
    def render(self, surface):
        for layer in self.tmx_data.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    tile = self.tmx_data.get_tile_image_by_gid(gid)
                    if tile:
                        surface.blit(
                            tile,
                            (x * self.tmx_data.tilewidth, y * self.tmx_data.tileheight)
                        )
                        
                        
class Decoration(pygame.sprite.Sprite):
    def __init__(self, image, pos, layer=0):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(topleft=pos)
        self._layer = layer