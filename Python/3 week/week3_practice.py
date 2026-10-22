def show_status(player):
    for key, value in player.items():
        print(key, ":", value)

# TODO 1: Define show_inventory(inventory).

# TODO 2: Define battle(player, enemy_name, enemy_hp, enemy_attack).
# Use while, if/elif/else, and return True/False.

player = {"name": input("Character name: "), "hp": 100, "gold": 30, "attack": 15}
inventory = ["potion"]

show_status(player)
# TODO 3: Call battle().
# TODO 4: If the player wins, add gold and an item.
