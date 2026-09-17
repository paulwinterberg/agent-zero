# Interaktive Items in Tiled erstellen

Dieses Dokument erklärt, wie du interaktive Items (Interactible Items) in Tiled erstellst, die der Spieler mit der **F-Taste** aktivieren kann.

## System-Übersicht

Das Spiel hat ein `InteractionManager`-System, das:
- Alle Objekte in der Nähe des Spielers erkennt
- Die nächsten Interaktionsziele priorisiert
- Auf Tastendruck (F) reagiert

## Schritte zum Erstellen von Interaktiven Items

### 1. **Object Layer in Tiled vorbereiten**

Stelle sicher, dass du eine Object Layer mit dem Namen **"Objects"** hast:
- Öffne deine `.tmx` Datei in Tiled
- Sollte bereits vorhanden sein, sonst: Layer → New Layer → Object Layer
- Benenne sie zu "Objects"

### 2. **Ein interaktives Objekt hinzufügen**

1. Wähle das **Object Selection Tool** (oben links)
2. Ziehe mit der Maus ein Rechteck für dein interaktives Objekt
3. Das Objekt wird in der Object Layer erstellt

### 3. **Objekt als "Interactible" markieren**

Wähle dein Objekt in der Object Layer und:

**Option A: Mit Tile-Object (empfohlen für visuell)**
- Klicke auf das Objekt
- Im Properties-Panel: "Klasse" (oder "Type") auf **"Interactible"** setzen
- Optional: Gib dem Objekt einen Namen (z.B. "Door", "Chest", "NPC")

**Option B: Mit Custom Class**
- Rechtsklick auf das Objekt
- Classes → Interactible zuweisen

### 4. **Objekt benennen (optional aber empfohlen)**

Im Properties-Panel:
- **Name**: Gib dem Objekt einen eindeutigen Namen, z.B. "Door_MainHall", "Chest_Gold"
- Dieser Name wird beim Interagieren ausgegeben

### 5. **Zusätzliche Eigenschaften (optional)**

Du kannst Custom Properties hinzufügen für weitere Funktionen:
- **Description**: "Press F to open door"
- **InteractionType**: "door", "chest", "npc", etc.
- Weitere Properties nach Bedarf

## Beispiel in Tiled

```
Objects Layer:
├─ Door_Entrance (Class: Interactible)
├─ Chest_Gold (Class: Interactible)
└─ NPC_Guard (Class: Interactible)
```

## Programmierung: Interaktionen verarbeiten

Die Standard-Interaktion gibt nur den Namen aus. Um spezialisierte Interaktionen zu programmieren:

**In `main/states/gameplay.py`:**

```python
def _handle_interaction(self):
    """Behandelt spezifische Interaktionen."""
    nearest = self.interaction_manager.get_nearest_interaction()
    if nearest:
        name = nearest['name']
        
        if name == "Door_Entrance":
            print("Door wird geöffnet...")
            # Türlogik hier
        elif name == "Chest_Gold":
            print("Truhe wird geöffnet...")
            # Truhenlogik hier
        elif name == "NPC_Guard":
            print("Dialog mit Wache startet...")
            # Dialog-System hier
```

## Interaktionsbereich anpassen

Die **Reichweite** für Interaktionen kannst du in `main/core/interactions.py` ändern:

```python
class InteractionManager:
    def __init__(self):
        self.interaction_range = 50  # In Pixeln - hier ändern!
```

## Visuelles Feedback (optional)

Um dem Spieler zu zeigen, welche Objekte interaktiv sind:

1. In der `render_world` Funktion kannst du den nächsten Interaktionsziele anzeigen
2. Ein UI-Element "Press F to interact" rendern
3. Eine Highlight-Box um interaktive Objekte zeichnen

## Troubleshooting

### Objekt wird nicht als Interactible erkannt
- ✓ Überprüfe, dass die Class auf "Interactible" gesetzt ist
- ✓ Stelle sicher, dass das Objekt ein **Tile-Object** ist (nicht nur eine Form)
- ✓ Überprüfe den Namen der Object Layer ("Objects")

### Interaktion funktioniert nicht
- ✓ Drücke **F** während der Spieler nah am Objekt ist (≤50 Pixel)
- ✓ Schaue in der Konsole ob der Name ausgegeben wird
- ✓ Überprüfe den Abstand mit `self.interaction_manager.interaction_range`

### Mehrere Objekte gruppieren
Objekte mit dem **gleichen Namen** werden als ein Objekt behandelt - perfekt für:
- Türen mit mehreren Teilen
- Mehrteiliges Inventar-System
- Zusammenhängende Objekte

