import discord
from discord.ext import commands, tasks
import discord.errors
from discord_components import *
from source.db import Session
from source.config import PULLS_PER_DAY, COMMAND_PREFIX, RARITY_CHANCE
from source.verify import verify_mentioned, get_user
from source.models.user import User
from source.models.set import Set
from source.models.card import Card
from source.models.card_level import CardLevel
from datetime import datetime
import random
import asyncio
import threading


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

    return random.choice(card_list)


async def pull_cards(self, ctx, user_id, check_pull=False, count=PULLS_PER_DAY):
    session = Session()

    # check if User object exists, and create one if not
    my_user = get_user(session, user_id)

    # checks if user has a pull available if necessary
    if check_pull:
        if my_user.pull_available is False:
            await ctx.send(f'No pull available, resets at 0:00 GMT')
            return False
        my_user.pull_available = False

    # get a list of randomized cards to be added, and highest rarity
    card_list = []
    rarity = 1
    for _ in range(count):
        while True:
            card = roll(session, my_user.days_since_legend)
            if card not in card_list:
                card_list.append(card)
                break
        if card.rarity.value > rarity:
            rarity = card.rarity.value
        if card.rarity.name == 'legendary':
            my_user.days_since_legend = 0

    # Updates the CardInstance table, and post the card name and rarity for the user
    slot_file = discord.File(f'./media/images/slotmachine_{rarity}.gif')
    await ctx.send(file=slot_file)

    # Create the list of buttons (1 per card), display the card names, update user's collection
    buttons = [[]]
    for c in card_list:
        buttons[0].append(Button(style=ButtonStyle.blue, label=c.title))
        my_user.add_to_deck(session, c.id, 1)
        await ctx.send(f'You found a **{c.title}** [*{c.rarity.name}*]!')

    # Display the buttons, and the message which will be edited to hold images
    session.commit()
    m_but = await ctx.send("\nClick to view card.", components=buttons)
    m_img_exist = False

    # TODO Better functionality with threading
    x = threading.Thread()
    x.start()
    while True:
        def check(b):
            return ctx.author == b.author

        try:
            res = await self.bot.wait_for("button_click", timeout=30)
        except asyncio.TimeoutError:
            await m_but.delete()
            return

        try:
            await res.respond(type=6)
        except Exception as e:
            await m_but.delete()
            return

        res_text = res.component.label
        if m_img_exist:
            await m_img.delete()

        for i in range(len(card_list)):
            if res_text == card_list[i].title:
                buttons[0][i] = Button(style=ButtonStyle.green, label=card_list[i].title)
                # TODO
                q_level = session.query(CardLevel).filter(CardLevel.card_id == card_list[i].id,
                                                          CardLevel.level == 1).one()
                file = discord.File(q_level.artPath)
                m_img = await ctx.send(file=file)
            else:
                buttons[0][i] = Button(style=ButtonStyle.blue, label=card_list[i].title)
            m_img_exist = True
        await m_but.edit(components=buttons)


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
        await pull_cards(self, ctx, user_id, check_pull=True)

    @commands.command(name="freepull", aliases=['freep', 'FREEPULL'])
    async def free_pull(self, ctx, quantity):
        command = f"```{COMMAND_PREFIX}freePull [quantity] @user```"

        if not quantity.isdigit() or (int(quantity) < 0 or int(quantity) > 5):
            await ctx.send('Quantity must be between 0 and 7.\n' + command)
            return

        mentioned_user = await verify_mentioned(ctx, command)
        if mentioned_user is False:
            return

        await pull_cards(self, ctx, str(mentioned_user.id), check_pull=False, count=int(quantity))


def setup(bot):
    bot.add_cog(Pull(bot))
