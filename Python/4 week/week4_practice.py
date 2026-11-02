"""WEEK 4 BUILD SHEET - add persistent save/load to your Week 3 game.

Reuse the actual Week 3 functions. Insert the new function definitions ABOVE
your main menu, then add Save/Load options to that existing menu.

Required text-file format (one field per line, in EXACT order):
name, job, hp, gold, attack, defense, location, inventory_count,
then one line per inventory item. Do NOT save the rooms tuple.
"""

def save_game(filename, player, inventory):
    """TODO: Use with open(..., 'w'), write(), str(), and a for loop."""
    pass

def load_game(filename):
    """TODO: Use readlines or readline, strip(), int(), and a loop.

    Return a NEW (player_dictionary, inventory_list) pair.
    """
    pass

# TODO 1: Add Save and Load commands to the EXISTING Week 3 main menu.
# TODO 2: Create a distinct filename, e.g. 'savegame.txt'.
# TODO 3: When Load is selected, replace the current player and inventory.
# TODO 4: A missing save file must show a message rather than crash.
# TODO 5: Save, stop and restart the program, then load the same state.
# TODO 6: Retest battle, exploration, and shop AFTER loading.

# TEST BEFORE SUBMISSION:
# [ ] Save and reload two or more different inventory items.
# [ ] Name, job, HP, gold, attack, defense and location are identical.
# [ ] All numeric values are integers after loading.
# [ ] Missing file is handled cleanly.
# [ ] Existing Week 1-3 behavior still works.

# EARLY FINISHER: Add a second save slot or reject corrupted files gracefully.
