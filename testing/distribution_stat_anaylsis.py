# This file is to simulate card spread and pull rates
# Top values are adjustable to achieve the optimal results

cards_per_full_upgrade = 1+2+3+4+5+5+5
# Rarity: [standard, rare, legendary]
pulls_per_day = 1
card_per_pull = 5

packs_per_rare = 1
packs_per_legend = 7

# Card Amount
standard_amt = 36
rare_amt = 16
legendary_amt = 4

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Chance that any given card fragment is of that rarity
card_ratio = {"standard": 1 - ((1 / (packs_per_rare * card_per_pull)) + (1 / (packs_per_legend * card_per_pull))),
              "rare": 1 / (packs_per_rare * card_per_pull),
              "legendary": 1 / (packs_per_legend * card_per_pull)}

# Total card fragments needed to fully upgrade each card of that rarity.
# Assumes uniform distribution.
totalCardsNeeded = {"standard": cards_per_full_upgrade * standard_amt,
                    "rare": cards_per_full_upgrade * rare_amt,
                    "legendary": cards_per_full_upgrade * legendary_amt}

# Total packs needed to fully upgrade each card of that rarity.
# Assumes uniform distribution
totalPullsNeeded = {"standard": totalCardsNeeded["standard"] / card_ratio["standard"],
                    "rare": totalCardsNeeded["rare"] / card_ratio["rare"],
                    "legendary": totalCardsNeeded["legendary"] / card_ratio["legendary"]}


print("\nChance of any card fragment being of the respective rarity")
print("standard:\t" + str("{0:.3f}".format(card_ratio["standard"])))
print("rare:\t\t" + str("{0:.3f}".format(card_ratio["rare"])))
print("legendary:\t" + str("{0:.3f}".format(card_ratio["legendary"])))

print("\nTotal card fragments needed to fully upgrade each card of the respective rarity")
print("standard:\t" + str(totalCardsNeeded["standard"]))
print("rare:\t\t" + str(totalCardsNeeded["rare"]))
print("legendary:\t" + str(totalCardsNeeded["legendary"]))

print("\nTotal packs needed to fully upgrade rarity set")
print("standard:\t" + str(int(totalPullsNeeded["standard"] / (pulls_per_day * card_per_pull))))
print("rare:\t\t" + str(int(totalPullsNeeded["rare"] / (pulls_per_day * card_per_pull))))
print("legendary:\t" + str(int(totalPullsNeeded["legendary"] / (pulls_per_day * card_per_pull))))

print("\nTotal cards gained per 30 day month assuming no days were missed: " + str(pulls_per_day * card_per_pull * 30))