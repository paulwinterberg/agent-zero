import pygame
import pyscroll
import pytmx
import settings

class TileMap:
    def __init__(self, filename):
        tmx_data = pytmx.util_pygame.load_pygame(filename)
        self.tmx_data = tmx_data
        self.width = tmx_data.width * tmx_data.tilewidth
        self.height = tmx_data.height * tmx_data.tileheight
        self.collision_rects = self._load_collisions()
        self.decorations = self._load_decorations()

        map_data = pyscroll.data.TiledMapData(tmx_data)
        self.map_layer = pyscroll.orthographic.BufferedRenderer(
            map_data,
            (settings.DISPLAY_SIZE[0], settings.DISPLAY_SIZE[1])
        )
        self.map_layer.zoom = 2.0

    def _load_collisions(self):
        rects = []
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
        return rects

    def _load_decorations(self):
        decorations = []
        layer = self.tmx_data.get_layer_by_name("Decorations")
        for x, y, gid in layer:
            if gid == 0:
                continue
            image = self.tmx_data.get_tile_image_by_gid(gid)
            if image:
                pos = (x * self.tmx_data.tilewidth, y * self.tmx_data.tileheight)
                decorations.append(Decoration(image, pos))
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
    def __init__(self, image, pos):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(topleft=pos)
        # sort key: bottom of sprite = its "feet" position
        self._layer = self.rect.bottom