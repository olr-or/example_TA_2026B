import game_utils

class Character:
    def __init__(self, name, hp=100, gold=30, attack=15):
        # TODO 1: Save arguments to self.
        # TODO 2: Create self.inventory.
        pass

    def to_dict(self):
        # TODO 3: Return character data as a dictionary.
        pass

    def update_from_dict(self, data):
        # TODO 4: Update object attributes from data.
        pass

    def show(self):
        # TODO 5: Use game_utils functions.
        pass

hero = Character(input("Character name: "))
hero.show()

# TODO 6: Connect hero to game_utils.battle().
# TODO 7: Save the final state.
