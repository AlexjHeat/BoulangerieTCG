from discord.ext import commands




def verify_card(card):
    pass
    # TODO check if card is in database as name or id, if not then send error message and return false


def verify_card_name(card_name):
    pass
    # TODO check if cardname length is within range set by config.py


def verify_rarity(rarity):
    pass
    # TODO check if rarity is in enum list


def verify_type(type):
    pass
    # TODO check if type is in enum list


def verify_level(level):
    pass
    # TODO check if level is between 0 and 7


def verify_flavor(flavor):
    pass
    # TODO check if flavor length is within range set by config.py


def verify_stats(stats, rarity=False, card=False):
    pass
    # TODO check if stat total is within range set by config, using either the value for rarity or card


# TODO verify image function

def verify(ctx, card=False, card_name=False, rarity=False, type=False, level=False, flavor=False, stats=False):
    if card:
        if not verify_card(card):
            await ctx.send("Card id/name does not exist.")
            return False

    if card_name:
        if not verify_card_name(card_name):
            await ctx.send("Card name must be ___ characters or less.")
            return False

    if rarity:
        if not verify_rarity(rarity):
            await ctx.send("Rarity is invalid.")
            return False

    if type:
        if not verify_type(type):
            await ctx.send("Type is invalid.")
            return False

    if level:
        if not verify_level(level):
            await ctx.send("level must be between 0 and 7.")
            return False

    if flavor:
        if not verify_flavor(flavor):
            await ctx.send("Flavor must be ___ characters or less")
            return False

    if stats:
        if not verify_stats(stats, card=card, stat=stats):
            await ctx.send("Statsdsf.")
            return False


