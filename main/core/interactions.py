import pygame


class InteractionManager:
    """Verwaltet Spieler-Interaktionen mit Items in der Welt."""
    
    def __init__(self):
        self.active_interactions = []
        self.last_interaction_target = None
        self.interaction_range = 50  # Pixels
        self.interaction_cooldown = 0
        self.interaction_cooldown_time = 0.3  # Sekunden
        self.interactible_instances = {}  # Cache für Interactible-Instanzen
        self.tilemap = None
    
    def update(self, dt, player, tilemap):
        """Aktualisiert Interaktionsstatus und prüft auf neue Interaktionen."""
        self.tilemap = tilemap  # Speichere tilemap für Interactibles
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
    
    def try_interact(self):
        """Versucht mit dem nächsten Objekt in Reichweite zu interagieren."""
        if not self.active_interactions or self.interaction_cooldown > 0:
            return False
        
        closest = self.active_interactions[0]
        self.interaction_cooldown = self.interaction_cooldown_time
        self.last_interaction_target = closest
        
        # Lade Interactible und rufe on_interact auf
        interactible = self._load_interactible(closest)
        if interactible:
            interactible.on_interact()
        
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
            if "sprites" in interaction_obj:
                instance.set_sprites(interaction_obj["sprites"], interaction_obj.get("properties"))
            if hasattr(instance, 'set_tilemap'):
                instance.set_tilemap(self.tilemap)
            
            self.interactible_instances[obj_name] = instance
            return instance
            
        except (ImportError, AttributeError) as e:
            print(f"Fehler beim Laden von '{obj_name}': {e}")
            return None

    
    def get_nearest_interaction(self):
        """Gibt das nächste interaktive Objekt zurück oder None."""
        return self.active_interactions[0] if self.active_interactions else None

