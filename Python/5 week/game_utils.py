def show_status(player):
    print("\n[Status]")
    print("Name  :", player["name"])
    print("HP    :", player["hp"])
    print("Gold  :", player["gold"])
    print("Attack:", player["attack"])

def show_inventory(inventory):
    print("\n[Inventory]")
    if len(inventory) == 0:
        print("(empty)")
    else:
        for item in inventory:
            print("-", item)

def battle(player, enemy_name, enemy_hp, enemy_attack):
    print("\nA", enemy_name, "appeared!")
    while enemy_hp > 0 and player["hp"] > 0:
        print("Your HP:", player["hp"], "/", enemy_name, "HP:", enemy_hp)
        action = input("Attack or run? (a/r): ")

        if action == "a":
            enemy_hp -= player["attack"]
            print("You attacked for", player["attack"])
            if enemy_hp > 0:
                player["hp"] -= enemy_attack
                print(enemy_name, "attacked for", enemy_attack)
        elif action == "r":
            print("You escaped.")
            return False
        else:
            print("Choose a or r.")

    if player["hp"] > 0:
        print("You defeated", enemy_name)
        return True

    print("You were defeated.")
    return False

def save_game(filename, player, inventory):
    with open(filename, "w") as fp:
        fp.write(player["name"] + "\n")
        fp.write(str(player["hp"]) + "\n")
        fp.write(str(player["gold"]) + "\n")
        fp.write(str(player["attack"]) + "\n")
        for item in inventory:
            fp.write(item + "\n")

def load_game(filename):
    with open(filename, "r") as fp:
        name = fp.readline().strip()
        hp = int(fp.readline())
        gold = int(fp.readline())
        attack = int(fp.readline())
        inventory = []
        while True:
            line = fp.readline()
            if not line:
                break
            inventory.append(line.strip())
    return {"name": name, "hp": hp, "gold": gold, "attack": attack}, inventory
