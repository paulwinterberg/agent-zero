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
        self.objects, self.tall_objects, self._object_groups = self._load_y_sorted_objects()
        self.door_collision_rects = self._load_door_collisions()
        self.collision_rects.extend(self.door_collision_rects)

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

    def _get_object_layer(self, preferred_names):
        names = [preferred_names] if isinstance(preferred_names, str) else preferred_names
        for name in names:
            if not name:
                continue
            try:
                layer = self.tmx_data.get_layer_by_name(name)
            except ValueError:
                continue
            if isinstance(layer, pytmx.TiledObjectGroup):
                return layer
        return None

    def get_object(self, layer_name, object_name) -> pytmx.TiledObject | None:
        layer = self._get_object_layer([layer_name])
        if layer is None:
            return None
        for obj in layer:
            if obj.name == object_name:
                return obj
        return None

    def get_tool_spawns(self):
        """Return named tool spawn points from the Toolspawn object layer."""
        layer = self._get_object_layer("Toolspawn")
        if layer is None:
            return []
        return [
            {"name": obj.name, "position": (obj.x, obj.y)}
            for obj in layer
            if obj.name and not obj.gid
        ]

    def _load_door_collisions(self):
        """Create closed-door colliders for doors in the Objects layer."""
        door_collisions = []
        for group in self._object_groups.values():
            interaction_member = group["interaction_member"]
            if (
                interaction_member is not None
                and interaction_member.properties.get("InteractibleClass")
                in ("Door", "ContainerDoor")
            ):
                door_collisions.append(group["interaction_bounds"].copy())
        return door_collisions

    def get_layer_index(self, layer_name):
        for i, layer in enumerate(self.tmx_data.visible_layers):
            if layer.name == layer_name:
                return i
        return None

    def get_interactible_objects(self):
        """Return each interactible object group, including its Tiled properties."""
        interactibles = []

        for group in self._object_groups.values():
            if not any(sprite.alive() for sprite in group["sprites"]):
                continue

            interaction_member = group["interaction_member"]
            if interaction_member is None:
                continue

            interactibles.append({
                "name": group["interaction_name"],
                "rect": group["interaction_bounds"],
                "sprites": group["sprites"],
                "properties": dict(interaction_member.properties),
            })

        return interactibles


    def get_interactible_object(self, object_name):
        """Return a named interactible object, or None if it doesn't exist."""
        for obj in self.get_interactible_objects():
            if obj["name"] == object_name:
                return obj

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
    
        # Tile-property colliders on tile-objects placed in the
        # 'objects' layer (e.g. a tree or rock whose collision shape
        # was drawn in the tileset editor, not as a box in the
        # Collisions layer). obj.x/obj.y are already top-left — see
        # _load_y_sorted_objects — so the collider offsets from the
        # tileset apply directly, no grid-cell math needed.
        objects_layer = self._get_object_layer([TILED_OBJECTS_LAYER_NAME, "Objektebene", "Objects", "objects"])

        if isinstance(objects_layer, pytmx.TiledObjectGroup):
            for obj in objects_layer:
                if not obj.gid:
                    continue
                props = self.tmx_data.get_tile_properties_by_gid(obj.gid)
                if not props or not props.get("colliders"):
                    continue
                for collider in props["colliders"]:
                    rects.append(pygame.Rect(
                        obj.x + collider.x,
                        obj.y + collider.y,
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
        layer = self._get_object_layer([TILED_OBJECTS_LAYER_NAME, "Objektebene", "Objects", "objects"])
        if layer is None:
            return [], [], {}

        groups = {}
        for obj in layer:
            if not obj.gid:
                continue
            image = self.tmx_data.get_tile_image_by_gid(obj.gid)
            if not image:
                continue
            is_seethrough = bool(obj.properties.get("Seethrough"))
            key = id(obj) if is_seethrough or not obj.name else obj.name
            groups.setdefault(key, []).append((obj, image))

        for name, members in list(groups.items()):
            if (
                not isinstance(name, str)
                or not any(obj.properties.get("InteractibleClass") for obj, _ in members)
            ):
                continue

            remaining = set(range(len(members)))
            components = []
            while remaining:
                pending = [remaining.pop()]
                component = []
                while pending:
                    index = pending.pop()
                    component.append(members[index])
                    rect = pygame.Rect(
                        members[index][0].x,
                        members[index][0].y,
                        members[index][0].width,
                        members[index][0].height,
                    ).inflate(2, 2)
                    neighbors = [
                        other_index
                        for other_index in remaining
                        if rect.colliderect(pygame.Rect(
                            members[other_index][0].x,
                            members[other_index][0].y,
                            members[other_index][0].width,
                            members[other_index][0].height,
                        ))
                    ]
                    for neighbor in neighbors:
                        remaining.remove(neighbor)
                    pending.extend(neighbors)
                components.append(component)

            if len(components) > 1:
                del groups[name]
                for component in components:
                    component_id = min(obj.id for obj, _ in component)
                    groups[f"{name}_{component_id}"] = component

        flat_sprites = []
        tall_objects = []
        object_groups = {}

        for key, members in groups.items():
            member_rects = [pygame.Rect(obj.x, obj.y, obj.width, obj.height) for obj, _ in members]
            bounds = member_rects[0].unionall(member_rects[1:])

            bottom_offset = 0
            for obj, _ in members:
                offset = obj.properties.get("BottomOffset")
                if offset is not None:
                    bottom_offset = offset
                    break

            sort_y = bounds.bottom - bottom_offset
            sort_layer = self.y_sort_layer(sort_y)

            is_seethrough = any(
                obj.properties.get("Seethrough") for obj, _ in members
            )
            is_tall = (
                is_seethrough
                or bounds.height
                > self.tmx_data.tileheight * TILED_TALL_OBJECT_TILE_THRESHOLD
            )

            group_sprites = []
            for obj, image in members:
                sprite_image = image.copy() if is_tall else image
                group_sprites.append(Object(sprite_image, (obj.x, obj.y), sort_layer))

            flat_sprites.extend(group_sprites)

            if is_tall:
                tall_objects.append(YSortedObject(group_sprites, bounds, sort_layer))

            # Use the lowest member for sorting, while interaction metadata
            # comes only from members explicitly marked as interactibles.
            bottom_member = max((obj for obj, _ in members), key=lambda o: o.y + o.height)
            interaction_members = [
                obj for obj, _ in members
                if obj.properties.get("InteractibleClass")
            ]
            interaction_member = (
                max(interaction_members, key=lambda obj: obj.y + obj.height)
                if interaction_members else None
            )
            interaction_rects = [
                pygame.Rect(obj.x, obj.y, obj.width, obj.height)
                for obj in interaction_members
            ]
            interaction_bounds = (
                interaction_rects[0].unionall(interaction_rects[1:])
                if len(interaction_rects) > 1
                else interaction_rects[0] if interaction_rects
                else None
            )
            object_groups[key] = {
                "sprites": group_sprites,
                "bounds": bounds,
                "bottom_member": bottom_member,
                "interaction_name": key if isinstance(key, str) else bottom_member.name,
                "interaction_member": interaction_member,
                "interaction_bounds": interaction_bounds,
            }

        return flat_sprites, tall_objects, object_groups


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