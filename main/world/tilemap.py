import pygame
import pyscroll
import pytmx

from settings import TILED_OBJECTS_LAYER_NAME, TILED_OBJECT_OCCLUSION_ALPHA, TILED_OCCLUSION_FADE_SPEED, TILED_TALL_OBJECT_TILE_THRESHOLD


class TileMap:
    def __init__(self, filename, zoom_level=1.0):
        tmx_data = pytmx.util_pygame.load_pygame(filename)
        self.tmx_data = tmx_data
        self.width = tmx_data.width * tmx_data.tilewidth
        self.height = tmx_data.height * tmx_data.tileheight

        # All tile layers (Floor, Decorations, Walls, whatever else)
        # render flat via pyscroll's normal background pass now — none
        # of them are hidden or turned into sprites anymore. The only
        # y-sorted depth comes from the 'objects' object layer (see
        # _load_y_sorted_objects) plus the player.
        #
        # sort_base_layer just needs to sit above every tile layer so
        # y-sorted sprites always draw on top of the flat map.
        self.sort_base_layer = len(list(tmx_data.visible_layers))

        self.collision_rects = self._load_collisions()
        self.objects, self.tall_objects = self._load_y_sorted_objects()

        map_data = pyscroll.data.TiledMapData(tmx_data)
        self.map_layer = pyscroll.orthographic.BufferedRenderer(
            map_data,
            pygame.display.get_desktop_sizes()[0]
        )
        self.map_layer.zoom = zoom_level

    def y_sort_layer(self, pixel_y):
        """Fractional pyscroll layer, monotonic in pixel_y, always
        above every flat tile layer. Used for the player and for
        sprites built from the 'objects' layer, so they all sort
        against each other purely by depth."""
        return self.sort_base_layer + (pixel_y / self.tmx_data.tileheight)

    def zoom_to(self, zoom_level):
        self.map_layer.zoom = zoom_level

    def update_occlusion(self, player, dt):
        """Fade any tall object that currently hides the player: it
        must be drawn in front of the player (same comparison the
        y-sort draw order uses) AND overlap the player's rect on
        screen. Call this once per frame, before drawing."""
        player_sort = self.y_sort_layer(player.rect.bottom)

        for obj in self.tall_objects:
            drawn_in_front = obj.sort_layer > player_sort
            overlapping = obj.rect.colliderect(player.rect)
            obj.update(dt, drawn_in_front and overlapping)

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

        # Tile-property colliders (e.g. a wall tile flagged with a
        # "colliders" property in the tileset).
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

        # Explicit collision rectangles drawn in Tiled.
        try:
            collision_layer = self.tmx_data.get_layer_by_name("Collisions")
        except ValueError:
            collision_layer = None

        if isinstance(collision_layer, pytmx.TiledObjectGroup):
            for obj in collision_layer:
                rects.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))

        return rects

    def _load_y_sorted_objects(self):
        """Build Decoration sprites from the 'objects' object layer.
    
        Objects sharing a name are treated as one composite object
        (e.g. a tree made of several tile-objects): they're grouped
        together and all sort as a single unit, keyed off the lowest
        member of the group (the one with the greatest bottom-y).
        Unnamed objects each sort independently.
    
        A member tile-object may carry a custom "BottomOffset"
        property (set in Tiled on whichever tile-object forms the
        visual base of the group, e.g. a tree trunk under a canopy
        that overhangs past the trunk's actual ground contact point).
        When present, it shifts the y-coordinate used for sorting up
        from the group's true bounding-box bottom by that many pixels,
        so the player is drawn in front as soon as they pass the
        object's real base rather than the bottom of its (possibly
        taller-looking) artwork. It has no effect on the group's
        bounding rect, which is still used as-is for occlusion overlap
        checks against the player.
    
        Note: pytmx normalizes tile-object y to top-left on parse
        (Tiled itself stores tile-object y as the bottom edge), so
        obj.y is already a top-left coordinate and obj.y + obj.height
        is the bottom edge — no manual adjustment needed here.
        """
        try:
            layer = self.tmx_data.get_layer_by_name(TILED_OBJECTS_LAYER_NAME)
        except ValueError:
            return [], []
    
        if not isinstance(layer, pytmx.TiledObjectGroup):
            return [], []
    
        groups = {}
        for obj in layer:
            if not obj.gid:
                # Only tile-objects (objects with an image) are
                # rendered as sprites here; plain rectangles/points
                # in this layer, if any, are skipped.
                continue
            image = self.tmx_data.get_tile_image_by_gid(obj.gid)
            if not image:
                continue
            key = obj.name if obj.name else id(obj)
            groups.setdefault(key, []).append((obj, image))
    
        flat_sprites = []
        tall_objects = []
    
        for members in groups.values():
            member_rects = [pygame.Rect(obj.x, obj.y, obj.width, obj.height) for obj, _ in members]
            bounds = member_rects[0].unionall(member_rects[1:])
    
            # Look for a BottomOffset override on any member (there
            # should be at most one per group — it belongs to whichever
            # tile-object is the group's visual base).
            bottom_offset = 0
            for obj, _ in members:
                offset = obj.properties.get("BottomOffset")
                if offset is not None:
                    bottom_offset = offset
                    break
                
            sort_y = bounds.bottom - bottom_offset
            sort_layer = self.y_sort_layer(sort_y)
    
            is_tall = bounds.height > self.tmx_data.tileheight * TILED_TALL_OBJECT_TILE_THRESHOLD
    
            group_sprites = []
            for obj, image in members:
                # Tall objects get their own copy of the tile image
                # so fading one for occlusion doesn't bleed into
                # every other object sharing the same source gid.
                sprite_image = image.copy() if is_tall else image
                group_sprites.append(Object(sprite_image, (obj.x, obj.y), sort_layer))
    
            flat_sprites.extend(group_sprites)
    
            if is_tall:
                tall_objects.append(YSortedObject(group_sprites, bounds, sort_layer))
    
        return flat_sprites, tall_objects


class Object(pygame.sprite.Sprite):
    def __init__(self, image, pos, layer=0):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(topleft=pos)
        self._layer = layer


class YSortedObject:
    """A named group of Decoration sprites from the 'objects' layer,
    tracked as a unit so it can fade in/out as a whole when it's
    tall enough to hide the player behind it."""

    def __init__(self, sprites, rect, sort_layer):
        self.sprites = sprites
        self.rect = rect
        self.sort_layer = sort_layer
        self.alpha = 255.0
        self.target_alpha = 255.0

    def update(self, dt, occluding):
        self.target_alpha = TILED_OBJECT_OCCLUSION_ALPHA if occluding else 255
        if self.alpha == self.target_alpha:
            return

        step = TILED_OCCLUSION_FADE_SPEED * dt
        if self.alpha < self.target_alpha:
            self.alpha = min(self.alpha + step, self.target_alpha)
        else:
            self.alpha = max(self.alpha - step, self.target_alpha)

        for sprite in self.sprites:
            sprite.image.set_alpha(int(self.alpha))