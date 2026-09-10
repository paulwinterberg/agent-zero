import pygame


class InteractionManager:
    """Verwaltet Spieler-Interaktionen mit Items in der Welt."""
    
    def __init__(self):
        self.active_interactions = []
        self.last_interaction_target = None
        self.interaction_range = 50  # Pixels
        self.interaction_cooldown = 0
        self.interaction_cooldown_time = 0.3  # Sekunden
    
    def update(self, dt, player, tilemap):
        """Aktualisiert Interaktionsstatus und prüft auf neue Interaktionen."""
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
        
        # Setze Cooldown
        self.interaction_cooldown = self.interaction_cooldown_time
        self.last_interaction_target = closest
        
        # Lade und rufe die richtige Interactible-Klasse auf
        self._execute_interaction(closest)
        
        return True
    
    def _execute_interaction(self, interaction_obj):
        """Führt die passende Interaktion automatisch aus basierend auf InteractibleClass.
        
        Erwartet ein 'InteractibleClass' Custom Property in Tiled.
        
        Beispiele in Tiled Custom Properties:
        - InteractibleClass: "Curtains" -> lädt world.interactibles.curtains.Curtains
        - InteractibleClass: "Door" -> lädt world.interactibles.door.Door
        - InteractibleClass: "Chest" -> lädt world.interactibles.chest.Chest
        """
        print(interaction_obj)
        obj_name = interaction_obj.get("name", "Unknown")
        print(f"[INTERACTION] Interagiert mit: {obj_name}")
        
        try:
            # Hole die Klassennamen aus dem Custom Property
            class_name = interaction_obj["properties"].get("InteractibleClass")
            
            if not class_name:
                print(f"❌ Fehler: '{obj_name}' hat kein 'InteractibleClass' Custom Property")
                return
            
            module_name = class_name.lower()
            
            # Importiere dynamisch: from world.interactibles.{module_name} import {class_name}
            module = __import__(f"world.interactibles.{module_name}", fromlist=[class_name])
            interactible_class = getattr(module, class_name)
            
            # Instantiiere und rufe on_interact() auf
            instance = interactible_class()
            instance.on_interact()
            
        except (ImportError, AttributeError) as e:
            print(f"❌ Fehler: Konnte '{obj_name}' nicht laden - {e}")
        except Exception as e:
            print(f"❌ Fehler bei Interaktion mit '{obj_name}': {e}")

    
    def get_nearest_interaction(self):
        """Gibt das nächste interaktive Objekt zurück oder None."""
        return self.active_interactions[0] if self.active_interactions else None

