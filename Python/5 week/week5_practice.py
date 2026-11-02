"""WEEK 5 BUILD SHEET - refactor your COMPLETE Week 4 RPG.

Create your own game_utils.py using the functions YOU built in Weeks 3-4.
Your previous game must still work after the refactor. This file is a
STRUCTURAL HINT, not a ready-to-run final solution.

For Jupyter: game_utils.py must be a real file in the working directory if
you want to practice 'import game_utils'. A cell alone isn't a module import.
"""

import game_utils  # First CREATE game_utils.py from your own Week 3-4 code.

class Character:
    def __init__(self, name, job, hp, gold, attack, defense,
                 location="town", inventory=None):
    # TODO 1: Store all values in self.<attribute>.
    # TODO 2: Make a NEW list when inventory is None.
        pass

    def to_dict(self):
    # TODO 3: Return the player fields expected by game_utils functions.
        pass

    def update_from_dict(self, data):
    # TODO 4: Sync updated HP, gold, location and other fields back to self.
        pass

    def show(self):
    # TODO 5: Use your game_utils status/inventory functions.
        pass

# TODO 6: Add New Game / Load Game startup choices.
# TODO 7: Keep your Week 4 menu with status, inventory, explore, battle,
#         shop, save and exit. Use the Character object for game state.
# TODO 8: Make battle update the SAME hero after each fight.
# TODO 9: Save and load job, defense, location, inventory and all statistics.
# TODO 10: Run all Week 1-4 regression checks AFTER refactoring.

# TEST BEFORE SUBMISSION:
# [ ] Two character jobs have different starting attack/defense.
# [ ] Battle updates persist in the Character object and saved file.
# [ ] Module imports without errors from the SAME folder.
# [ ] Restart + Load restores the whole game state.
# [ ] Every Week 1-4 feature still works.

# EARLY FINISHER: Add Character.use_item() or a location-based enemy selector.
