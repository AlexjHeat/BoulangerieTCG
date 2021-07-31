import discord
from discord.ext import commands
from source.db import Session
from source.config import PULLS_PER_DAY, COMMAND_PREFIX, RARITY_CHANCE
from source.models.user import User
from source.models.set import Set
from source.models.card import Card
from source.models.card_instance import CardInstance
import random


def roll(session, legendary_mult):
    RARITY_CHANCE[2] *= legendary_mult

    # Randomly determine rarity based on config.py
    x = random.randint(1, sum(RARITY_CHANCE))
    if x < RARITY_CHANCE[0]:
        rarity = 'standard'
    elif x < RARITY_CHANCE[0] + RARITY_CHANCE[1]:
        rarity = 'rare'
    else:
        rarity = 'legendary'

    # gets appropriate card list based on whether a set is boosted and has the determined rarity
    boosted = session.query(Set).filter(Set.boosted).one_or_none()
    card_list = session.query(Card).filter(Card.rarity == rarity).all()
    if boosted is not None and x % 2 == 0:
        card_list = session.query(Card).filter(Card.rarity.name == rarity, Card.set == boosted.prefix).all()
        if card_list is None:
            card_list = session.query(Card).filter(Card.rarity == rarity).all()

    #returns random item from card list
    return random.choice(card_list)



async def pull_cards(ctx, user_id, checkPull=False, count=PULLS_PER_DAY):
    session = Session()

    # check if User object exists, and create one if not
    my_user = session.query(User).filter(User.id == user_id).one_or_none()
    if my_user is None:
        my_user = User(id=user_id, wins=0, losses=0, days_since_legend=0, pull_available=True, deck_private=False)
        session.add(my_user)

    # checks if user has a pull available if necessary
    if checkPull:
        if my_user.pull_available is False:
            await ctx.send(f'No pull available, resets at 0:00 GMT')
            return False
        my_user.pull_available = False

    # send a slot machine gif
    slot_file = discord.File('./media/images/slotmachine.gif')
    await ctx.send(file=slot_file)

    # get a list of randomized cards to be added
    card_list = []
    for _ in range(count):
        while True:
            card = roll(session, my_user.days_since_legend)
            if card not in card_list:
                card_list.append(card)
                break
        if card.rarity.name == 'legendary':
            my_user.days_since_legend = 0

    # Updates the CardInstance table, and creates new rows if necessary
    for c in card_list:
        q = session.query(CardInstance).filter(CardInstance.user_id == my_user.id,
                                               CardInstance.card_id == c.id).one_or_none()
        if q is None:
            session.add(CardInstance(user_id=my_user.id, card_id=c.id, level=0, quantity=1, active=False))
        else:
            q.quantity += 1

    # Post the card name and rarity for the user
    # TODO: write algorithm that creates fragmented images of the level 1 cards, resize them to be smaller
    for c in card_list:
        if c.rarity.name == 'legendary':
            await ctx.send(f'Woah! You found a :starsflux:**{c.title}**:starsflux: [{c.rarity.name}]!')
        else:
            await ctx.send(f'You found a **{c.title}** [{c.rarity.name}]!')
    session.commit()


class Pull(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command(aliases=['p', 'P', 'PULL', 'pull'])
    async def Pull(self, ctx):
        user_id = str(ctx.message.author.id)
        await pull_cards(ctx, user_id, checkPull=True)


    @commands.command(aliases=['freepull'])
    async def FreePull(self, ctx, quantity):
        command = f"```{COMMAND_PREFIX}freePull [quantity] @user```"

        if not quantity.isdigit() or (int(quantity) < 0 or int(quantity) > 7):
            await ctx.send('Quantity must be between 0 and 7.\n' + command)
            return

        if len(ctx.message.mentions) != 1:
            await ctx.send('Need to @ a user.' + command)
            return

        user_id = str(ctx.message.mentions[0].id)
        await pull_cards(ctx, user_id, checkPull=False, count=int(quantity))


def setup(bot):
    bot.add_cog(Pull(bot))
