import random

# 0 = no advantage, 1 = p1 advantage, 2 = p2 advantage

advantage = 2
p1_stat = 75
p2_stat = 120
number_of_tests = 1000000


# Advantage takes the higher die, disadvantage takes the lower
def battle_sim1(n, p1, p2, adv):
    x = p1 + p2
    p1_victory_count = 0
    for _ in range(n):
        die1 = random.randint(1, x)
        die2 = random.randint(1, x)

        if adv == 1:
            p1_total = p1 + max(die1, die2)
            p2_total = p2 + min(die1, die2)
        elif adv == 2:
            p1_total = p1 + min(die1, die2)
            p2_total = p2 + max(die1, die2)
        else:
            p1_total = p1 + die1
            p2_total = p2 + die2

        if p1_total > p2_total:
            p1_victory_count += 1

    return p1_victory_count / n


# Advantage re-rolls the die as in dnd5e, disadvantage has no alteration
def battle_sim2(n, p1, p2, adv):
    x = p1 + p2
    p1_victory_count = 0
    for _ in range(n):
        if adv == 1:
            die1 = max(random.randint(1, x), random.randint(1, x))
            die2 = random.randint(1, x)
        elif adv == 2:
            die1 = random.randint(1, x)
            die2 = max(random.randint(1, x), random.randint(1, x))
        else:
            die1 = random.randint(1, x)
            die2 = random.randint(1, x)

        p1_total = p1 + die1
        p2_total = p2 + die2
        if p1_total > p2_total:
            p1_victory_count += 1
    return p1_victory_count / n


print("Advantage takes higher:\t" + str(battle_sim1(number_of_tests, p1_stat, p2_stat, advantage)))
print("Advantage re-rolls:\t" + str(battle_sim2(number_of_tests, p1_stat, p2_stat, advantage)))