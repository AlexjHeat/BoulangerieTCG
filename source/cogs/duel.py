import asyncio
import discord
from discord.ext import commands
from source.db import Session
from source.config import COMMAND_PREFIX
from source.verify import verify_mentioned, get_card, get_user
from source.models.card import Card
from source.duel_block import DuelBlock, Duelist


def get_title(session, card_level):
    card = session.query(Card).filter(Card.id == card_level.card_id).one()
    return card.title


def get_house(session, card_level):
    card = session.query(Card).filter(Card.id == card_level.card_id).one()
    return card.house.name


class Duel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['DUEL'])
    @commands.max_concurrency(1)
    async def duel(self, ctx):
        command = f'```{COMMAND_PREFIX}duel @user```'

        # Get both users for the trade
        user1 = ctx.author
        user2 = await verify_mentioned(ctx, command)
        if user2 is False:
            return False

        # If either duelist has no active cards, cancel duel and explain
        duel_block = DuelBlock(user1, user2)
        if len(duel_block.user1.active) == 0:
            await ctx.send(f'{duel_block.user1.name} has no active cards.')
            return
        if len(duel_block.user2.active) == 0:
            await ctx.send(f'{duel_block.user2.name} has no active cards.')
            return

        # Send embed + buttons and wait for responses
        m = await ctx.send(file=duel_block.file, embed=duel_block.embed, components=duel_block.buttons)

        while duel_block.user1.attack is None or duel_block.user2.attack is None:
            duel_block.user2.attack = 'Post'

            def check(b):
                if b.channel == ctx.channel:
                    return b.author == user1 or b.channel == user2

            button = await self.bot.wait_for("button_click", check=check, timeout=180)
            await button.respond(type=6)

            # Process the button response
            if button.component.label == 'Cancel':
                await ctx.send('Duel canceled.')
                await m.edit(components=[])
                return
            duel_block.process_button(button)

        # Calculate damage
        duel_block.duel()

        # Begin duel messages
        file = discord.File('./media/images/duel.gif')
        await ctx.send(file=file)
        await asyncio.sleep(2)
        m = await ctx.send('Duel in 3 seconds...')
        await asyncio.sleep(1)
        await m.edit('Duel in 2 seconds...')
        await asyncio.sleep(1)
        await m.edit('Duel in 1 seconds...')
        await asyncio.sleep(1)

        # Send damage messages
        await ctx.send(f'{duel_block.user1.name}  {duel_block.user1.attack}s for {duel_block.user1} damage!')
        await asyncio.sleep(2)
        await ctx.send(f'{duel_block.user2.name}  {duel_block.user2.attack}s for {duel_block.user2} damage!')
        await ctx.send(f'{duel_block.get_winner()} has won the duel!')
        await m.edit(components=[])


    @commands.command()
    async def activate(self, ctx, *cards):
        command = f'```{COMMAND_PREFIX}a [card id/title] [card id/title] [card id/title]```'

        # Check args, max of 3
        if len(cards) > 3:
            await ctx.send(f"You may only activate *up to* 3 cards at a time.\n{command}")
            return

        session = Session()

        # Get user and clear their active cards
        my_user = get_user(session, str(ctx.author.id))
        my_user.clear_active(session)

        # Verify that args are valid cards, set active if the user has a leveled version of one
        for card in cards:
            my_card = await get_card(session, ctx, card)
            if my_card is not False:
                if my_user.set_active(session, my_card.id) is False:
                    await ctx.send(f"You do not own a leveled **{my_card.title}**.")

        # Get list of user's active cards, as CardLevel objects
        active_list = my_user.get_active(session)

        # Verify that the active list contains at least one valid card
        if len(active_list) == 0:
            session.rollback()
            return

        # Verify that the active cards are of the same house
        house = active_list[0].get_house(session)
        for c_level in active_list:
            if house != c_level.get_house(session):
                session.rollback()
                await ctx.send(f"All active cards must be from the same house.")
                return

        # Craft confirmation message
        msg = f'Lv{active_list[0].level} **{ active_list[0].get_title(session)}**'
        for card in active_list[1:]:
            msg += f',  Lv{card.level} **{card.get_title(session)}**'

        if len(active_list) == 1:
            msg += ' is '
        else:
            msg += ' are '
        msg += f'now active!'
        session.commit()
        await ctx.send(msg)


def setup(bot):
    bot.add_cog(Duel(bot))
