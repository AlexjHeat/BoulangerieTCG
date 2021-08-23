import asyncio

import discord
from discord.ext import commands
from discord_components import *
from source.db import Session
from source.config import COMMAND_PREFIX, MAX_TITLE_LENGTH
from source.verify import get_card, get_user, verify_level
from source.models.card_instance import CardInstance
from source.models.card_level import CardLevel


class CardList:
    def __init__(self, id, title, house, level, quantity, post, lurk, react):
        self.id = id
        self.title = title
        self.house = house
        self.level = str(level)
        self.quantity = str(quantity)
        self.post = str(post)
        self.lurk = str(lurk)
        self.react = str(react)

    def __lt__(self, other):
        if self.house != other.house:
            return self.house < other.house
        return self.id < other.id

    def __eq__(self, other):
        return self.id == other.id

async def get_listview(card_list, index):
    id_w = 6
    title_w = MAX_TITLE_LENGTH
    house_w = 10
    level_w = 6
    amount_w = 9
    stat_w = 5

    msg = f"```elm\n{'ID'.ljust(id_w)}{'Title'.ljust(title_w)}{'House'.ljust(house_w)}{'LVL'.ljust(level_w)}" \
          f"{'Amount'.ljust(amount_w)}{'Post'.ljust(stat_w)}{'Lurk'.ljust(stat_w)}{'React'.ljust(stat_w)}\n"

    for card in card_list[index:index+15]:
        msg += f"{card.id.ljust(id_w)}{card.title.ljust(title_w).lower()}{card.house.ljust(house_w)}" \
               f"{card.level.ljust(level_w)}{card.quantity.ljust(amount_w)}{card.post.ljust(stat_w)}" \
               f"{card.lurk.ljust(stat_w)}{card.react.ljust(stat_w)}\n"

    msg += f'\nCards ({index + 1} - {min(index + 16, len(card_list))})```'
    return msg


class View(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['VIEW', 'v', 'V'])
    async def view(self, ctx, card_id, level='1'):
        command = f"```{COMMAND_PREFIX}view [card id/title] [level]```"
        session = Session()

        my_card = await get_card(session, ctx, card_id, command=command)
        if my_card is False:
            return

        if await verify_level(ctx, level) is False:
            return

        file = discord.File(f'./media/cards/{my_card.id}_{level}.png')
        await ctx.send(file=file)

    @commands.command(aliases=['DECK', 'd', 'D'])
    async def deck(self, ctx):
        session = Session()
        my_user = get_user(session, str(ctx.author.id))

        # Get list of all cards owned by user
        my_user_list = session.query(CardInstance).filter(CardInstance.user_id == my_user.id).all()

        # Use my_user_list to create CardList objects with the necessary info for deck view
        view_list = []
        for card in my_user_list:
            if card.level != 0 or card.quantity != 0:
                my_level = session.query(CardLevel).filter(CardLevel.card_id == card.card_id,
                                                           CardLevel.level == card.level).one()
                view_list.append(CardList(card.card_id, my_level.get_title(session), my_level.get_house(session),
                                          card.level, card.quantity, my_level.post, my_level.lurk, my_level.react))

        # TODO: verify that sort works
        view_list = sorted(view_list)

        # Define the buttons
        buttons = [[Button(style=ButtonStyle.blue, label="First"),
                    Button(style=ButtonStyle.blue, label="Previous"),
                    Button(style=ButtonStyle.blue, label="Next"),
                    Button(style=ButtonStyle.blue, label="Last")]]

        # Post the first 15 cards
        index = 0
        msg = await ctx.send(await get_listview(view_list, index), components=buttons)

        while True:
            # Get the button response
            def check(b):
                return b.channel == ctx.channel
            try:
                button = await self.bot.wait_for("button_click", check=check, timeout=100)
            except asyncio.TimeoutError:
                return
            res = button.component.label
            await button.respond(type=6)

            # Change the index according to the button response
            if res == 'First':
                index = 0
            elif res == 'Previous':
                index = max(index - 15, 0)
            elif res == 'Next':
                index = min(index + 15, len(view_list) - 1)
            elif res == 'Last':
                index = max(0, len(view_list) - 15)

            # Edit message
            await msg.edit(await get_listview(view_list, index))


def setup(bot):
    bot.add_cog(View(bot))
