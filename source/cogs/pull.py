import discord
from discord.ext import commands, tasks
from source.db import Session
from source.config import PULLS_PER_DAY, COMMAND_PREFIX, RARITY_CHANCE
from source.verify import verify_mentioned, get_user
from source.models.user import User
from source.models.set import Set
from source.models.card import Card
from datetime import datetime
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

    # TODO make it so that the boosted set chance is exactly 50, maybe...
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
    my_user = get_user(session, user_id)

    # checks if user has a pull available if necessary
    if checkPull:
        if my_user.pull_available is False:
            await ctx.send(f'No pull available, resets at 0:00 GMT')
            return False
        my_user.pull_available = False

    # TODO send a different slot machine gif depending on rarities pulled
    # send a slot machine gif
    slot_file = discord.File('./media/images/slotmachine.gif')
    await ctx.send("message message", file=slot_file)

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
        my_user.add_to_collection(session, c.id)

    # Post the card name and rarity for the user
    # TODO: write algorithm that creates fragmented images of the level 1 cards, resize them to be smaller
    for c in card_list:
        if c.rarity.name == 'legendary':
            await ctx.send(f'Pog, you found a :starsflux:**{c.title}**:starsflux: [{c.rarity.name}]!')
        else:
            await ctx.send(f'You found a **{c.title}** [{c.rarity.name}]!')

    # TODO: Button to view cards (only view one card at a time)
    session.commit()


def refresh():
    session = Session()
    user_list = session.query(User).all()
    for u in user_list:
        u.pull_available = True
        if u.days_since_legend < 15:
            u.days_since_legend += 1
    session.commit()


class Pull(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.refresh.start()

    @tasks.loop(minutes=1)
    async def refresh(self):
        now = datetime.now()
        if now.hour == 21 and now.minute == 00:
            refresh()
            print(f'user pulls refreshed at {now.hour}:{now.minute}')

    @commands.command(name='pull', aliases=['p', 'P', 'PULL', 'Pull'])
    async def pull(self, ctx):
        user_id = str(ctx.message.author.id)
        await pull_cards(ctx, user_id, checkPull=True)


    @commands.command(name="freepull", aliases=['freep', 'FREEPULL'])
    async def free_pull(self, ctx, quantity):
        command = f"```{COMMAND_PREFIX}freePull [quantity] @user```"

        if not quantity.isdigit() or (int(quantity) < 0 or int(quantity) > 7):
            await ctx.send('Quantity must be between 0 and 7.\n' + command)
            return

        mentioned_user = await verify_mentioned(ctx, command)
        if mentioned_user is False:
            return

        await pull_cards(ctx, str(mentioned_user.id), checkPull=False, count=int(quantity))

def setup(bot):
    bot.add_cog(Pull(bot))
