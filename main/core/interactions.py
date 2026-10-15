import pygame
from world.interactibles.button import Button
from world.interactibles.door import Door


class InteractionManager:
    """Verwaltet Spieler-Interaktionen mit Items in der Welt."""
    
    def __init__(self):
        self.active_interactions = []
        self.last_interaction_target = None
        self.interaction_range = 70  # Pixels
        self.interaction_cooldown = 0
        self.interaction_cooldown_time = 0.3  # Sekunden
        self.interactible_instances = {}  # Cache für Interactible-Instanzen
        self.tilemap = None
        self.feedback_message = None
        self._doors_initialized = False

    def initialize_doors(self, tilemap):
        self.tilemap = tilemap
        if self._doors_initialized:
            return

        for obj in tilemap.get_interactible_objects():
            if obj["properties"].get("InteractibleClass") in (
                "Door",
                "ContainerDoor",
            ):
                self._load_interactible(obj)

        for door_name in Door.PUZZLE_DOOR_NAMES:
            self.get_interactible_instance(door_name)
        self._doors_initialized = True
    
    def update(self, dt, player, tilemap):
        """Aktualisiert Interaktionsstatus und prüft auf neue Interaktionen."""
        self.initialize_doors(tilemap)
        self.interaction_cooldown = max(0, self.interaction_cooldown - dt)
        
        # Finde alle interaktiven Objekte in Reichweite
        self.active_interactions = self._get_nearby_interactions(player, tilemap)
    
    def _get_nearby_interactions(self, player, tilemap):
        """Gibt alle interaktiven Objekte in Reichweite des Spielers zurück."""
        nearby = []
        interactible_objects = tilemap.get_interactible_objects()
        
        for obj in interactible_objects:
            distance = self._distance_to_object(player, obj)
            if distance <= self.interaction_range:
                nearby.append({
                    **obj,
                    "distance": distance
                })
        
        nearby.sort(key=lambda x: x["distance"])
        return nearby
    
    def _distance_to_object(self, player, obj):
        """Berechnet Entfernung vom Spieler zu Objekt."""
        player_center = player.rect.center
        obj_center = obj["rect"].center
        dx = player_center[0] - obj_center[0]
        dy = player_center[1] - obj_center[1]
        return (dx**2 + dy**2) ** 0.5
    
    def try_interact(self, held_tool=None):
        """Versucht mit dem nächsten Objekt in Reichweite zu interagieren."""
        self.feedback_message = None
        if not self.active_interactions or self.interaction_cooldown > 0:
            return False
        
        closest = min(
            self.active_interactions,
            key=lambda interaction: (
                interaction.get("sort_layer", 0),
                interaction["distance"],
            ),
        )
        self.interaction_cooldown = self.interaction_cooldown_time
        self.last_interaction_target = closest
        
        # Lade Interactible und rufe on_interact auf
        interactible = self._load_interactible(closest)
        if interactible:
            interacted = interactible.on_interact(held_tool)
            if isinstance(interactible, Door):
                if (
                    interactible.state == "closed"
                    and interactible.locked
                    and not getattr(held_tool, "can_unlock", False)
                ):
                    self.feedback_message = "Tür ist verschlossen."
                elif interacted and interactible.state == "open":
                    self.feedback_message = "Tür geöffnet."
            elif isinstance(interactible, Button) and interacted:
                door = self.get_interactible_instance(interactible.opens_door)
                if isinstance(door, Door) and door.state == "open":
                    self.feedback_message = "Tür geöffnet."
                else:
                    self.feedback_message = "Knopf gedrückt. Finde den zweiten Knopf."
        
        return True
    
    def _load_interactible(self, interaction_obj):
        """Lädt oder cached eine Interactible-Instanz basierend auf 'InteractibleClass' Property."""
        obj_name = interaction_obj.get("name", "Unknown")
        
        if obj_name in self.interactible_instances:
            return self.interactible_instances[obj_name]
        
        try:
            class_name = interaction_obj["properties"].get("InteractibleClass")
            if not class_name:
                return None
            
            # Dynamischer Import: world.interactibles.{classname_lowercase}.{ClassName}
            module_name = class_name.lower()
            module = __import__(f"world.interactibles.{module_name}", fromlist=[class_name])
            interactible_class = getattr(module, class_name)
            
            # Instanz erstellen und konfigurieren
            instance = interactible_class()
            if hasattr(instance, "set_object_name"):
                instance.set_object_name(obj_name)
            if "sprites" in interaction_obj:
                instance.set_sprites(interaction_obj["sprites"], interaction_obj.get("properties"))
            if hasattr(instance, 'set_tilemap'):
                instance.set_tilemap(self.tilemap)
            if hasattr(instance, "set_interaction_manager"):
                instance.set_interaction_manager(self)
            
            self.interactible_instances[obj_name] = instance
            return instance
            
        except (ImportError, AttributeError) as e:
            print(f"Fehler beim Laden von '{obj_name}': {e}")
            return None

    
    def get_nearest_interaction(self):
        """Gibt das nächste interaktive Objekt zurück oder None."""
        return self.active_interactions[0] if self.active_interactions else None

    def get_interactible_instance(self, object_name):
        """Return the cached instance for a named interactible object."""
        if not self.tilemap:
            return None

        interaction_obj = self.tilemap.get_interactible_object(object_name)
        if interaction_obj is None:
            return None
        return self._load_interactible(interaction_obj)

    def are_buttons_for_door_pushed(self, door_name):
        """Return whether every button assigned to a door has been pushed."""
        if not self.tilemap:
            return False

        required_button_names = Button.BUTTON_GROUPS.get(door_name)
        if required_button_names is None:
            buttons = [
                obj for obj in self.tilemap.get_interactible_objects()
                if obj["properties"].get("InteractibleClass") == "Button"
                and obj["properties"].get("OpensDoor") == door_name
            ]
            required_button_names = tuple(obj["name"] for obj in buttons)
        if not required_button_names:
            return False

        for button_name in required_button_names:
            button = self.get_interactible_instance(button_name)
            if not isinstance(button, Button):
                return False
            if not button.pushed:
                return False
        return True
