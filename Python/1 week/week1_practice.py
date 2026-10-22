print("=" * 42)
print("        YONSEI QUEST - Character Setup")
print("=" * 42)

name = input("Character name: ")
job = input("Choose job (warrior / mage): ")

hp = 100
gold = 30

if job == "warrior":
    attack = 15
    # TODO: set warrior defense
elif job == "mage":
    attack = 20
    # TODO: set mage defense
else:
    job = "traveler"
    attack = 10
    # TODO: set default defense

print()
print("[Character]")
print("Name   :", name)
print("Job    :", job)
print("HP     :", hp)
print("Attack :", attack)
print("Defense:", defense)
print("Gold   :", gold)

# TODO: Ask whether the player wants to buy a potion.
# TODO: If choice is y AND gold is at least 10, update gold and hp.
