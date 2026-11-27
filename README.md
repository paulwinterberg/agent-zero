# Repository_GK12_2024

Dies ist ein Softwareprojekt, das Python und Pygame verwendet. 
In diesem Projekt wollen wir ein Spiel erstellen, indem ein Geheimagent Agent 00 Missionen erfüllt.

# wichtige Links

https://trello.com/b/JXelqW3A/game #Projektideen
https://www.pixilart.com/draw #Assets erstellen


# To merge main branch into current branch:
git checkout <branchname> <br>
git fetch origin <br>
git merge origin/main <br>

# To run the code
open new codespace in browser: <br>
type "pip install -r requirements.txt" into terminal <br>
run code by inputting "python main/main.py" into terminal <br>

# In-game menus
Press ESC to open the pause menu, where you can access the shop and volume settings.
Enemy kills earn 50 coins. The shop sells ammunition for 300 coins, Pistol for
400 coins, Pistol+ for 1,000 coins, Pistol+max for 5,000 coins, Healing for 150
coins, Magic Powder for 400 coins, Energy for 150 coins, and Smoke Bombs for 200
coins. Healing, Magic Powder, and Smoke Bombs stack up to five. Use them with
right-click; Healing restores up to 50 health per use. Select Levels in the
ESC menu to load another level.

# How to Move and Interact
W = Move forward
A = Move left
S = Move backward
D = Move right
Q = Drop the current item
Hold Tab = Open the weapon wheel and select an item
E = Pick up a nearby item
F = Interact with a nearby door, container, or button
Left mouse button = Fire or use the equipped tool
Right mouse button = Use the equipped tool's secondary action, if available (Healing, Magic Powder)
Shift = Sprint
Strg = Slide while sprinting
R = Reload your pistol if you have ammunition in your inventory
Esc = Open the pause menu