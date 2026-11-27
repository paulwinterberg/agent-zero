class Level:
    COMPLETION_TUTORIAL_NAME = ""
    COMPLETION_FADE_DURATION = 1.0
    COMPLETION_MESSAGE_DURATION = 3.0
    COMPLETION_REWARD = 800
    
    AMBIENCE = None

    MESSAGES = {}
    DIALOGUE = ()

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
    COMPLETION_TUTORIAL_NAME = "End"

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

class AntarcticaLevel(Level):
    MESSAGES = {}

class BossBattleLevel(Level):
    MESSAGES = {}
    PHASE_DIALOGUES = {
        2: (
            ("AGENT X", "I need to know if I can trust you."),
            ("AGENT 0", "You called me here. Start talking."),
            (
                "AGENT X",
                "Not so fast. You've been working for MI6 for a long time. I need to see what you're capable of.",
            ),
            ("AGENT 0", "You want to continue the fight?"),
            ("AGENT X", "Consider it a test."),
        ),
        3: (
            ("AGENT 0", "Enough! What is this all about?"),
            ("AGENT X", "Your mission in Antarctica. Dr. Edward Frost."),
            (
                "AGENT 0",
                "I was ordered to capture him and destroy his research. That's all I know.",
            ),
            ("AGENT X", "That's exactly what they wanted you to believe."),
            ("AGENT 0", "What are you talking about?"),
            (
                "AGENT X",
                "Frost wasn't developing a weapon. His discovery, the Magic Powder, could have changed medicine forever. It had the potential to help cure diseases and save thousands of lives.",
            ),
            ("AGENT 0", "Then why did MI6 want it destroyed?"),
            (
                "AGENT X",
                "Because they couldn't control it. Their partners in the pharmaceutical industry stood to lose billions if a treatment like this became widely available.",
            ),
            ("AGENT 0", "So they made me destroy it?"),
            (
                "AGENT X",
                "They used you. They wanted Frost captured, his research erased, and the truth buried.",
            ),
            ("AGENT 0", "I don't believe you. Why should I trust a traitor?"),
            ("AGENT X", "Because I'm the only one telling you the truth."),
            ("AGENT 0", "Then prove it!"),
            ("AGENT X", "I was hoping you'd say that."),
        ),
        4: (
            (
                "MI6 RADIO",
                "Attention. Agent X has been located. All units, move in. Eliminate both targets.",
            ),
            ("AGENT 0", "Both targets? They're coming for me too?"),
            ("AGENT X", "Now do you believe me?"),
            ("AGENT 0", "I guess we have a common enemy."),
            (
                "AGENT X",
                "For now, we fight together. We can settle things between us later.",
            ),
            ("AGENT 0", "Deal."),
            ("AGENT X", "This contains the evidence. Everything MI6 tried to hide."),
            ("AGENT 0", "Then let's make sure they don't get it."),
            ("AGENT X", "Stay close. There are more of them coming."),
        ),
    }
    DIALOGUE = (
        ("AGENT 0", "What's this?"),
        (
            "MI6 RADIO",
            "Attention. All available agents. We have reason to believe that Agent X is somewhere in the area. Keep your eyes open. Do not approach without authorization.",
        ),
        ("AGENT 0", "Agent X?"),
        ("AGENT X", "I see you found my equipment."),
        ("AGENT 0", "Who is this?"),
        ("AGENT X", "Someone who has been trying to warn you."),
        ("AGENT 0", "Where are you?"),
        ("AGENT X", "Look around. I'm closer than you think."),
        (
            "AGENT X",
            "Before we talk, there's something you need to remember. Your mission in Antarctica. Dr. Edward Frost.",
        ),
        ("AGENT 0", "What about him?"),
        (
            "AGENT X",
            "You were told he was dangerous. But did you ever ask yourself why MI6 wanted him captured?",
        ),
        (
            "AGENT X",
            "We need to talk. But first, I need to know if I can trust you.",
        ),
    )

LEVELS = {
    "tutorial": TutorialIslandLevel,
    "containership": ContainershipLevel,
    "hq_lobby": HQLobbyLevel,
    "testlevel": TestLevel,
    "antarctica": AntarcticaLevel,
    "bossbattle": BossBattleLevel,
}