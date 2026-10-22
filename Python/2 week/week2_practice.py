name = input("Character name: ")
inventory = ["potion"]
player = {"name": name, "hp": 100, "gold": 30, "attack": 15}
rooms = ("town", "forest", "cave")

# TODO 1: Print every room using for.

while True:
    print("\n1. Show status")
    print("2. Show inventory")
    print("3. Find an item")
    print("4. Exit")
    menu = input("Select: ")

    # TODO 2: menu 1 - print player dictionary using items().
    # TODO 3: menu 2 - print every item.
    # TODO 4: menu 3 - input an item and append it.
    # TODO 5: menu 4 - break.
