"""WEEK 2 BUILD SHEET - extend your completed Week 1 project.

Do NOT run this file as a replacement game. Copy/adapt the relevant pieces
INTO your Week 1 code. Keep the real job, attack, defense, HP and gold.
The TODOs are deliberately not solved; design the menu yourself.
"""

# STEP 1 - ADD AFTER YOUR WEEK 1 CHARACTER SETUP.
# Do not use fixed values (e.g., attack=15) for every job.
# player = {
#     "name": name,
#     "job": job,
#     "hp": hp,
#     "gold": gold,
#     "attack": attack,
#     "defense": defense,
#     "location": "town",
# }
# inventory = ["potion"]
# rooms = ("town", "forest", "cave")

# STEP 2 - ADD A REPEATING MAIN MENU TO YOUR EXISTING GAME.
# TODO 1: Use while True and offer Status, Inventory, Explore, Shop, Exit.
# TODO 2: Print all player dictionary values using items() and a for loop.
# TODO 3: Print each inventory item using a for loop; handle an empty list.
# TODO 4: Explore: accept town/forest/cave; reject invalid locations.
# TODO 5: Update player["location"] when exploration succeeds.
# TODO 6: Forest -> herb; Cave -> key; don't add the same find twice.
# TODO 7: Keep the Week 1 potion shop, available only in town.
# TODO 8: Make invalid menu inputs return to the menu; Exit must break.

# TEST BEFORE SUBMISSION (do not hard-code test outcomes):
# [ ] Mage still has mage-specific attack and defense from Week 1.
# [ ] Visiting forest twice does NOT duplicate the herb.
# [ ] Shop is blocked in cave; it works in town with enough gold.
# [ ] Exit works and all earlier Week 1 features still work.

# EARLY FINISHER: Add a 5-item inventory limit and a 'use potion' action.
