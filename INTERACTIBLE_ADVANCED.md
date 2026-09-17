# Erweitertes Interaktions-System mit visuellen Hinweisen

Dieses ist ein optionales erweitertes System, um dem Spieler zu zeigen:
- Welche Items in Reichweite sind
- Welches Item am nächsten ist
- Ein visueller Hinweis "Press F to interact"

## Erweiterte Implementierung

### 1. Gameplay mit visuellem Feedback aktualisieren

**Datei: `main/states/gameplay.py`**

```python
import pygame
import settings

from entities.player import Player
from states.state import State
from core.renderer import load_tilemap, render_world
from core.interactions import InteractionManager


class Gameplay(State):
    def __init__(self):
        self.player = Player()
        self.tilemap, self.group = load_tilemap("assets/levels/hq_lobby.tmx", self.player)
        self.interaction_manager = InteractionManager()
        
        self.tilemap.zoom_to(4)
        
        spawnPoint = self.tilemap.get_object("Spawns", "PlayerSpawn")
        self.player.goto((spawnPoint.x, spawnPoint.y))
        
        # Font für UI
        self.ui_font = pygame.font.Font(None, 24)
    
    def update(self, dt, events):
        self.player.update(dt, self.tilemap)
        self.interaction_manager.update(dt, self.player, self.tilemap)
        
        # Prüfe auf F-Taste Druck für Interaktion
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == settings.INTERACT:
                    self._handle_interaction()
    
    def draw(self, screen, dt):
        render_world(dt, self.tilemap, self.group, self.player)
        
        # Zeichne Interaktions-UI
        self._draw_interaction_ui(screen)
    
    def _draw_interaction_ui(self, screen):
        """Zeichnet UI-Hinweise für verfügbare Interaktionen."""
        nearest = self.interaction_manager.get_nearest_interaction()
        
        if not nearest:
            return
        
        # Text "Press F to interact"
        text = self.ui_font.render("Press [F] to interact", True, (255, 255, 255))
        text_rect = text.get_rect(center=(screen.get_width() // 2, screen.get_height() - 50))
        
        # Schwarzer Hintergrund für bessere Lesbarkeit
        bg_rect = text_rect.inflate(20, 10)
        pygame.draw.rect(screen, (0, 0, 0), bg_rect)
        pygame.draw.rect(screen, (100, 255, 100), bg_rect, 2)  # Grüner Rahmen
        
        screen.blit(text, text_rect)
        
        # Optional: Name des Ziels anzeigen
        target_name = nearest.get('name', 'Unknown')
        name_text = self.ui_font.render(f"Target: {target_name}", True, (200, 200, 255))
        name_rect = name_text.get_rect(center=(screen.get_width() // 2, screen.get_height() - 80))
        screen.blit(name_text, name_rect)
    
    def _handle_interaction(self):
        """Behandelt spezifische Interaktionen."""
        nearest = self.interaction_manager.get_nearest_interaction()
        if nearest:
            name = nearest['name']
            print(f"[INTERACTION] Interagiert mit: {name}")
            
            # Spezifische Interaktionen basierend auf Namen
            if "door" in name.lower():
                self._interact_door(name)
            elif "chest" in name.lower():
                self._interact_chest(name)
            elif "npc" in name.lower():
                self._interact_npc(name)
            else:
                print(f"Keine spezifische Aktion für {name}")
    
    def _interact_door(self, door_name):
        """Behandelt Tür-Interaktionen."""
        print(f"🚪 Tür '{door_name}' wird geöffnet...")
        # Türlogik: Sound abspielen, Animation, Levelwechsel, etc.
    
    def _interact_chest(self, chest_name):
        """Behandelt Truhen-Interaktionen."""
        print(f"📦 Truhe '{chest_name}' wird geöffnet...")
        # Truhenlogik: Items zeigen, Sound, Animation, etc.
    
    def _interact_npc(self, npc_name):
        """Behandelt NPC-Interaktionen."""
        print(f"🗣️ Dialog mit '{npc_name}' startet...")
        # Dialog-System, Quest-System, etc.
```

### 2. Debug-Modus (optional)

Um alle Interaktionsziele zu sehen, füge dies zur `_draw_interaction_ui` hinzu:

```python
DEBUG_INTERACTIONS = True  # In settings.py oder hier

def _draw_interaction_ui(self, screen):
    """Zeichnet UI-Hinweise für verfügbare Interaktionen."""
    
    # DEBUG: Alle Interaktionen zeichnen
    if DEBUG_INTERACTIONS:
        for i, interaction in enumerate(self.interaction_manager.active_interactions):
            debug_text = self.ui_font.render(
                f"{i+1}. {interaction['name']} ({interaction['distance']:.0f}px)",
                True,
                (255, 100, 100)
            )
            screen.blit(debug_text, (10, 10 + i * 25))
    
    # Reste des Code...
```

## Verwendung in Tiled

1. **Object Layer "Objects" erstellen**
2. **Objekte mit Klasse "Interactible" markieren:**
   - Beispiele:
     - `Door_MainHall` (Class: Interactible)
     - `Chest_TreasureRoom` (Class: Interactible)
     - `NPC_GuardDuty` (Class: Interactible)

3. **Optional Custom Properties hinzufügen:**
   - `description`: "Opens the main hall"
   - `interactionType`: "door"
   - `targetLevel`: "hq_mainHall"

## Erweiterte Features

### Quest-Interaktionen

```python
def _interact_npc(self, npc_name):
    """NPC-Interaktion mit Quest-System."""
    if npc_name == "NPC_GuardDuty":
        if not self.player.has_completed_quest("intro_talk"):
            self._start_dialog("intro_talk")
        else:
            print("Bereits erledigt!")
```

### Inventar-Integration

```python
def _interact_chest(self, chest_name):
    """Truhe öffnen und Items hinzufügen."""
    items = ["Gold Coin", "Health Potion"]
    for item in items:
        self.player.inventory.add_item(item)
    print(f"Items aus {chest_name} hinzugefügt!")
```

## Fehlerbehebung

- **"Press F to interact" erscheint nicht:** Stelle sicher, dass `_draw_interaction_ui` in `draw()` aufgerufen wird
- **Keine Debug-Ausgaben:** Überprüfe die Konsole und stelle sicher, dass die Objekte die richtige Klasse haben
- **Zu große/kleine Reichweite:** Passe `interaction_range` in `InteractionManager.__init__()` an
