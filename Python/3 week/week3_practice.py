"""WEEK 3 BUILD SHEET - add battles to your completed Week 2 game.

Keep Week 1 character choices and Week 2 status/inventory/explore/shop.
Move reusable logic into functions; integrate into your EXISTING menu.
"""

def show_status(player):
    """TODO: Move your Week 2 dictionary display logic into this function."""
    pass

def show_inventory(inventory):
    """TODO: Move your Week 2 inventory display logic into this function."""
    pass

def battle(player, enemy_name, enemy_hp, enemy_attack):
    """TODO: Return True ONLY for victory; False for run or defeat.

    Each turn: show HP and ask (a)ttack, (d)efend, or (r)un.
    Attack: subtract player attack from enemy HP. A living enemy hits back.
    Defend: deal no damage; take max(1, enemy_attack - player defense).
    Run: end immediately with False. Invalid input: retry the choice.
    Changes to player['hp'] must persist after the battle.
    """
    pass

# TODO 1: Integrate show_status(), show_inventory(), and battle() into your EXISTING repeating menu.
# TODO 2: Call it for slime (35 HP, 10 attack) AND goblin (55 HP, 14 attack).
# TODO 3: Award 20 gold and the relevant item ONLY if battle() returns True.
#         Slime -> "slime jelly"; goblin -> "goblin coin".
# TODO 4: Keep Week 2 exploration/shop/status/inventory operational.
# TODO 5: Test win, run, defeat and invalid action scenarios.

# TEST BEFORE SUBMISSION:
# [ ] Warrior vs slime: victory after 3 attacks (15 attack each).
# [ ] Running away gives zero rewards.
# [ ] Defending reduces damage based on Week 1 defense.
# [ ] Both enemies use the same battle() function.
# [ ] After battle, the main menu still works.

# EARLY FINISHER: Add a usable potion inside battles; do not skip enemy turns.
