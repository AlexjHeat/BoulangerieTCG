from source.models.card_level import CardLevel
#from .models.card_level import CardLevel
import random


def pick_stat(stats):
    rand = random.randint(1, sum(stats))
    if rand <= stats[0]:
        return 0
    if rand <= stats[1]:
        return 1
    return 2
    # TODO: Make pick_stats() a bit more biased towards picking the higher stats, and a bit more even with even stats


def populate_stats(session, stats, my_card):
    q_level = session.query(CardLevel).filter(CardLevel.card_id == my_card.id, CardLevel.level == 1).one()
    q_level.post = stats[0]
    q_level.lurk = stats[1]
    q_level.react = stats[2]

    stat_ratio = []
    for i in range(len(stats)):
        stat_ratio.append(stats[i] / sum(stats))

    stat_total = my_card.rarity.value * 11
    if my_card.rarity.value == 1:
        stat_total += 2

    for lvl in range(2, 8):
        stat_total += 3 + my_card.rarity.value * (lvl - 1)

        q_level = session.query(CardLevel).filter(CardLevel.card_id == my_card.id, CardLevel.level == lvl).one()
        q_level.post = int(round(stat_total * stat_ratio[0]))
        q_level.lurk = int(round(stat_total * stat_ratio[1]))
        q_level.react = int(round(stat_total * stat_ratio[2]))

