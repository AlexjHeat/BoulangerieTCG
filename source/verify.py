from sqlalchemy import func
from source import config
from source.models.card import Card, HouseEnum, RarityEnum
from source.models.set import Set


def verify_card(session, card):
    card = card.upper()
    q_id = session.query(Card).filter(func.upper(Card.id) == card).one()
    q_title = session.query(Card).filter(func.upper(Card.title) == card).first()
    if q_id is not None:
        return q_id.id
    if q_title is not None:
        return q_title.id
    return False


async def verify_card_title(ctx, card_title):
    if len(card_title) > config.MAX_TITLE_LENGTH:
        await ctx.send(f'TITLE ERROR: Title must be less than {config.MAX_TITLE_LENGTH}')
        return False


async def verify_rarity(ctx, rarity):
    rarity_values = set(item.value for item in RarityEnum)
    if rarity.upper() not in rarity_values:
        await ctx.send(f'RARITY ERROR: **{rarity}** is not in the list {rarity_values}')
        return False


async def verify_type(ctx, type):
    type_values = set(item.value for item in HouseEnum)
    if type.upper() not in type_values:
        await ctx.send(f'RARITY ERROR: **{type}** is not in the list {type_values}')
        return False


async def verify_level(ctx, level):
    if level.isdigit():
        if int(level) >= 0 and int(level) <= 7:
            return
    await ctx.send(f'LEVEL ERROR: level must be between 0 and 7.')
    return False


async def verify_set(session, ctx, set):
    q = session.query(Card).filter(Set.prefix == set.upper()).one_or_none()
    if not session.query(q.exists()).scalar():
        await ctx.send(f'SET ERROR: **{set.upper()}** does not exist.')
        return False






"""
async def verify(session, ctx, card=False, card_title=False, rarity=False,
                 type=False, level=False, flavor=False, set=False):
    result = True
    if card:
        if not await verify_card(session, ctx, card):
            result = False
    if card_title:
        if not await verify_card_title(ctx, card_title):
            result = False
    if rarity:
        if not await verify_rarity(ctx, rarity):
            result = False
    if type:
        if not await verify_type(ctx, type):
            result = False
    if level:
        if not await verify_level(ctx, level):
            result = False
    if flavor:
        if not await verify_flavor(ctx, flavor):
            result = False
    if set:
        if not await verify_flavor(session, ctx, flavor):
            result = False
    return result
"""

