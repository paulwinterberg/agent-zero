class Level:
    COMPLETION_TUTORIAL_NAME = ""
    COMPLETION_FADE_DURATION = 1.0
    COMPLETION_MESSAGE_DURATION = 3.0
    COMPLETION_REWARD = 800
    
    AMBIENCE = None

    MESSAGES = {}

class TutorialIslandLevel(Level):
    COMPLETION_TUTORIAL_NAME = "TutorialEnd"
    
    AMBIENCE = "island_sounds.mp3"

    MESSAGES = {
       "1": (
           "You've been stranded in enemy territory. Find your way out of this island."
       ),
       "2": (
            "There are enemies lurking nearby. Pick up the gun and be quick to not alert them."
        ),
       "3": (
           "Press E to pick up the gun."
        ),
       "4": (
           "Enemies drop their weapons when killed. Pick it up and hold TAB to see your inventory."
        ),
       "5": (
           "Sometimes it's better to not be spotted at all. Press CONTROL while sprinting to slide past the enemies."
        )
    }

class ContainershipLevel(Level):
    COMPLETION_TUTORIAL_NAME = "ContainermapEnd"

    MESSAGES = {
        "ContainermapStart": (
            "Willkommen auf dem Containerschiff. Suche das Kokain, das die "
            "Schmuggler hier schmuggeln, und fliehe mit den Beweismitteln. "
            "Gehe nun nach links zur ersten Kreuzung und suche den grünen "
            "Container dort am Rand."
        ),
        "OpenContainer": (
            "Mit F kannst du den Container öffnen, falls er nicht verschlossen "
            "ist. Für die verschlossenen brauchst du einen Schlüssel, den du in "
            "einem gelben Container findest. Insgesamt gibt es 8 Container, die "
            "du öffnen kannst. Danach suchst du nach dem Knopf, der die "
            "Eisentür zur Kommandostelle öffnet. Kleiner Tipp: Einen Hinweis "
            "auf die Position der Container findest du bei den gelben Kränen."
            "Die sind hier ganz in der Nähe. Viel Glück!"
        ),
        "PressTheButton": (
            "Drücke den Knopf, damit die verschlossene Eisentür zur "
            "Kommandostelle aufspringt."
        ),
        "Komandostelle": (
            "Finde die 2 verborgenen Knöpfe, um die vorletzte Ebene "
            "freizuschalten. Viel Glück!"
        ),
        "NextStep": (
            "Fast geschafft! Du musst nur noch 2 Knöpfe finden und du bist "
            "fertig. Probiere nicht, getötet zu werden."
        ),
        "Brücke": (
            "Auf der Brücke wird das ganze Schiff gesteuert. Finde den Knopf, "
            "der hier verborgen ist."
        ),
        "FindExit": (
            "Nur noch ein letzter Schritt. Du bist schon ganz nah. Töte die "
            "Wachen und steig in den Container, um als blinder Passagier das "
            "Schiff zu verlassen."
        ),
    }

LEVELS = {
    "tutorial": TutorialIslandLevel,
    "containership": ContainershipLevel
}