from sqlalchemy import func
from source.models.card import Card
from source.models.set import Set
from source.models.user import User


def get_user(session, user_id):
    my_user = session.query(User).filter(User.id == user_id).one_or_none()
    if my_user is None:
        my_user = User(id=user_id, wins=0, losses=0, days_since_legend=0, pull_available=True, deck_private=False)
        session.add(my_user)
    return my_user


async def verify_card(session, ctx, card, command=None):
    q = session.query(Card).filter(Card.id == card.upper()).one_or_none()
    if q is None:
        q = session.query(Card).filter(func.upper(Card.title) == card.upper()).one_or_none()
    if q is None:
        await ctx.send(f'CARD ERROR: **{card}** does not exist.\n')
        if command:
            await ctx.send(command)
        return False
    return q


async def verify_mentioned(ctx, command=None):
    if len(ctx.message.mentions) == 1:
        return ctx.message.mentions[0]
    await ctx.send(f'USER ERROR: Must @user\n')
    if command:
        await ctx.send(command)
    return False


async def verify_set(session, ctx, prefix, command=None):
    q = session.query(Set).filter(Set.prefix == prefix.upper()).one_or_none()
    if q is None:
        await ctx.send(f'SET ERROR: **{prefix.upper()}** does not exist.')
        if command:
            await ctx.send(command)
        return False
    return q


async def verify_level(ctx, level):
    if level.isdigit():
        if int(level) >= 0 and int(level) <= 7:
            return
    await ctx.send(f'LEVEL ERROR: level must be between 0 and 7.')
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

