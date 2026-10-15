import heapq
import math

import pygame
import pyscroll
import pytmx

from settings import CAMERA_RENDER_SCALE, TILED_OBJECTS_LAYER_NAME, TILED_OBJECT_OCCLUSION_ALPHA, TILED_OCCLUSION_FADE_SPEED, TILED_TALL_OBJECT_TILE_THRESHOLD, TILED_SPAWNS_LAYER_NAME


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

        self.objects, self.tall_objects, self._object_groups = self._load_y_sorted_objects()
        self.collision_rects = self._load_collisions()

        map_data = pyscroll.data.TiledMapData(tmx_data)
        display = pygame.display.get_surface()
        screen_width, screen_height = (
            display.get_size()
            if display is not None
            else pygame.display.get_desktop_sizes()[0]
        )
        self.map_layer = pyscroll.orthographic.BufferedRenderer(
            map_data,
            (
                screen_width * CAMERA_RENDER_SCALE,
                screen_height * CAMERA_RENDER_SCALE,
            ),
        )
        self.map_layer.zoom = zoom_level * CAMERA_RENDER_SCALE

    def y_sort_layer(self, pixel_y):
        """Fractional pyscroll layer, monotonic in pixel_y, always
        above every flat tile layer. Used for the player and for
        sprites built from the 'objects' layer, so they all sort
        against each other purely by depth."""
        return self.sort_base_layer + (pixel_y / self.tmx_data.tileheight)

    def zoom_to(self, zoom_level):
        self.map_layer.zoom = zoom_level * CAMERA_RENDER_SCALE

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
                "sort_layer": group["sort_layer"],
            })

        return interactibles

    def get_layer_objects(self, layer_name):
        try:
            layer = self.tmx_data.get_layer_by_name(layer_name)
        except ValueError:
            return []
    
        if not isinstance(layer, pytmx.TiledObjectGroup):
            return []

        infos = []
        for obj in layer:
            infos.append({
                "name": obj.name,
                "type": obj.type,
                "properties": dict(obj.properties),
                "rect": pygame.Rect(obj.x, obj.y, obj.width, obj.height),
            })
    
        return infos

    def get_spawns(self):
        return self.get_layer_objects(TILED_SPAWNS_LAYER_NAME)

    def get_objects(self):
        return self.get_layer_objects(TILED_OBJECTS_LAYER_NAME)

    def get_interactible_object(self, object_name):
        """Return a named interactible object, or None if it doesn't exist."""
        for obj in self.get_interactible_objects():
            if obj["name"] == object_name:
                return obj

        return None


    def find_path(self, start, goal, hitbox_size):
        """Find a collision-free route between hitbox midbottom positions."""
        start = pygame.Vector2(start)
        goal = pygame.Vector2(goal)
        hitbox_width, hitbox_height = hitbox_size
        if hitbox_width <= 0 or hitbox_height <= 0:
            return []

        cell_size = max(1, min(self.tmx_data.tilewidth, self.tmx_data.tileheight) // 2)
        first_x = hitbox_width // 2
        last_x = self.width - (hitbox_width - first_x)
        first_y = hitbox_height
        if first_x > last_x or first_y > self.height:
            return []

        columns = (last_x - first_x) // cell_size + 1
        rows = (self.height - first_y) // cell_size + 1
        points = [
            (first_x + column * cell_size, first_y + row * cell_size)
            for row in range(rows)
            for column in range(columns)
        ]
        blocked = [False] * len(points)

        # Expand each collider into the equivalent forbidden area for the
        # enemy's midbottom anchor, then mark only grid cells it overlaps.
        for collider in self.collision_rects:
            left = collider.left - (hitbox_width - hitbox_width // 2) + 1
            right = collider.right + hitbox_width // 2
            top = collider.top + 1
            bottom = collider.bottom + hitbox_height
            min_column = max(0, math.ceil((left - first_x) / cell_size))
            max_column = min(columns, math.ceil((right - first_x) / cell_size))
            min_row = max(0, math.ceil((top - first_y) / cell_size))
            max_row = min(rows, math.ceil((bottom - first_y) / cell_size))
            for row in range(min_row, max_row):
                y = first_y + row * cell_size
                for column in range(min_column, max_column):
                    x = first_x + column * cell_size
                    if left <= x < right and top <= y < bottom:
                        blocked[row * columns + column] = True

        sample_spacing = max(1, cell_size // 4)
        probe = pygame.Rect(0, 0, hitbox_width, hitbox_height)

        def segment_is_clear(begin, end):
            distance = begin.distance_to(end)
            steps = max(1, math.ceil(distance / sample_spacing))
            probe.midbottom = (round(begin.x), round(begin.y))
            start_rect = probe.copy()
            probe.midbottom = (round(end.x), round(end.y))
            swept_rect = start_rect.union(probe)
            nearby_colliders = [
                rect for rect in self.collision_rects
                if rect.colliderect(swept_rect)
            ]
            for index in range(steps + 1):
                point = begin.lerp(end, index / steps)
                probe.midbottom = (round(point.x), round(point.y))
                if probe.left < 0 or probe.top < 0 or probe.right > self.width or probe.bottom > self.height:
                    return False
                if any(probe.colliderect(rect) for rect in nearby_colliders):
                    return False
            return True

        if segment_is_clear(start, goal):
            return [goal]

        start_column = round((start.x - first_x) / cell_size)
        start_row = round((start.y - first_y) / cell_size)
        start_nodes = []
        search_radius = 2
        for row in range(max(0, start_row - search_radius), min(rows, start_row + search_radius + 1)):
            for column in range(max(0, start_column - search_radius), min(columns, start_column + search_radius + 1)):
                node_index = row * columns + column
                if blocked[node_index]:
                    continue
                point = pygame.Vector2(points[node_index])
                if segment_is_clear(start, point):
                    start_nodes.append(((row, column), point, start.distance_to(point)))

        if not start_nodes:
            return []

        def point_for(node):
            row, column = node
            return pygame.Vector2(points[row * columns + column])

        target_tolerance = cell_size * 1.5
        costs = {}
        previous = {}
        open_nodes = []
        for node, point, cost in start_nodes:
            if cost < costs.get(node, math.inf):
                costs[node] = cost
                previous[node] = None
                heuristic = point.distance_to(goal)
                heapq.heappush(open_nodes, (cost + heuristic, cost, node))

        reached_node = None
        closest_node = None
        closest_distance = math.inf
        while open_nodes:
            _, current_cost, current = heapq.heappop(open_nodes)
            if current_cost != costs.get(current):
                continue
            current_point = point_for(current)
            distance_to_goal = current_point.distance_to(goal)
            if distance_to_goal < closest_distance:
                closest_node = current
                closest_distance = distance_to_goal
            if distance_to_goal <= target_tolerance and segment_is_clear(current_point, goal):
                reached_node = current
                break

            row, column = current
            for row_offset in (-1, 0, 1):
                for column_offset in (-1, 0, 1):
                    if row_offset == 0 and column_offset == 0:
                        continue
                    next_row = row + row_offset
                    next_column = column + column_offset
                    if not (0 <= next_row < rows and 0 <= next_column < columns):
                        continue
                    next_node = (next_row, next_column)
                    next_index = next_row * columns + next_column
                    if blocked[next_index]:
                        continue
                    if row_offset and column_offset:
                        if (blocked[row * columns + next_column]
                                or blocked[next_row * columns + column]):
                            continue

                    next_point = point_for(next_node)
                    if not segment_is_clear(current_point, next_point):
                        continue
                    step_cost = cell_size * (math.sqrt(2) if row_offset and column_offset else 1)
                    new_cost = current_cost + step_cost
                    if new_cost >= costs.get(next_node, math.inf):
                        continue
                    costs[next_node] = new_cost
                    previous[next_node] = current
                    heuristic = next_point.distance_to(goal)
                    heapq.heappush(open_nodes, (new_cost + heuristic, new_cost, next_node))

        if reached_node is None:
            reached_node = closest_node
        if reached_node is None:
            return []

        path = []
        node = reached_node
        while node is not None:
            path.append(point_for(node))
            node = previous[node]
        path.reverse()
        endpoint = path[-1]
        if endpoint.distance_squared_to(goal) > 0 and segment_is_clear(endpoint, goal):
            path.append(goal)
        return path

    
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

    def _remove_door_collisions(self, collisions):
        door_bounds = [
            group["bounds"]
            for group in self._object_groups.values()
            if group["interaction_member"] is not None
            and group["interaction_member"].properties.get("InteractibleClass")
            in ("Door", "ContainerDoor")
        ]
        filtered_collisions = []

        for collision in collisions:
            remaining = [collision]
            for door_bounds_rect in door_bounds:
                split_rects = []
                for rect in remaining:
                    overlap = rect.clip(door_bounds_rect)
                    if overlap.width == 0 or overlap.height == 0:
                        split_rects.append(rect)
                        continue

                    split_rects.extend(
                        piece
                        for piece in (
                            pygame.Rect(
                                rect.left,
                                rect.top,
                                rect.width,
                                overlap.top - rect.top,
                            ),
                            pygame.Rect(
                                rect.left,
                                overlap.bottom,
                                rect.width,
                                rect.bottom - overlap.bottom,
                            ),
                            pygame.Rect(
                                rect.left,
                                overlap.top,
                                overlap.left - rect.left,
                                overlap.height,
                            ),
                            pygame.Rect(
                                overlap.right,
                                overlap.top,
                                rect.right - overlap.right,
                                overlap.height,
                            ),
                        )
                        if piece.width > 0 and piece.height > 0
                    )
                remaining = split_rects
            filtered_collisions.extend(remaining)

        return filtered_collisions

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
                "sort_layer": sort_layer,
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
    """A named group of object sprites from the 'objects' layer,
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