
from source.config import MAX_STATS
from source.models.card_level import CardLevel
import random


def pick_stat(stats):
    rand = random.randint(1, sum(stats)**2)
    if rand <= stats[0]**2:
        return 0
    if rand <= stats[1]**2:
        return 1
    return 2
    # TODO: Make pick_stats() a bit more biased towards picking the higher stats


def populate_stats(session, stats, card_id):
    if sum(stats) <= MAX_STATS[0]:
        rarity = 1
    elif sum(stats) <= MAX_STATS[1]:
        rarity = 2
    elif sum(stats) <= MAX_STATS[2]:
        rarity = 3
    else:
        return False

    q_level = session.query(CardLevel).filter(CardLevel.card_id == card_id, CardLevel.level == 1).one()
    q_level.post = stats[0]
    q_level.lurk = stats[1]
    q_level.react = stats[2]

    increment = [1, 1, 1]
    for lvl in range(2, 8):
        for i in range(len(stats)):
            stats[i] += increment[i]
        for _ in range(rarity):
            i = pick_stat(stats)
            stats[i] += 1
            increment[i] += 1

        q_level = session.query(CardLevel).filter(CardLevel.card_id == card_id, CardLevel.level == lvl).one()
        q_level.post = stats[0]
        q_level.lurk = stats[1]
        q_level.react = stats[2]


