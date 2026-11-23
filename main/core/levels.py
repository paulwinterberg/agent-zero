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
            "Welcome aboard the container ship. Find the Magic Powder the smugglers "
            "are smuggling here and escape with the evidence. Head left to the first "
            "intersection and look for the green container at the edge."
        ),
        "OpenContainer": (
            "Press F to open a container if it isn't locked. Locked containers "
            "require a key, which you can find in a yellow container. There are "
            "8 containers you can open. Then look for the button that opens the "
            "iron door to the command center. Hint: The nearby yellow cranes will "
            "give you a clue about where the containers are. Good luck!"
        ),
        "PressTheButton": (
            "Press the button to unlock the iron door to the command center."
        ),
        "Komandostelle": (
            "Find the 2 hidden buttons to unlock the penultimate area. Good luck!"
        ),
        "NextStep": (
            "Almost there! You only need to find 2 more buttons. Try not to get killed."
        ),
        "Brücke": (
            "The entire ship is controlled from the bridge. Find the button hidden here."
        ),
        "FindExit": (
            "Just one last step. You're almost there. Take out the guards and climb "
            "into the container to leave the ship as a stowaway."
        ),
    }

class HQLobbyLevel(Level):
    MESSAGES = {}

class TestLevel(Level):
    MESSAGES = {}

LEVELS = {
    "tutorial": TutorialIslandLevel,
    "containership": ContainershipLevel,
    "hq_lobby": HQLobbyLevel,
    "testlevel": TestLevel,
}