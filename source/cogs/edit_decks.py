import discord
from discord.ext import commands
from discord_components import *
from source.verify import get_card, verify_mentioned, get_user
from source.db import Session
from source.config import COMMAND_PREFIX, ROLE_PERM

class AdminEdit(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['addfragment', 'ADDFRAGMENT', 'ADD', 'add'])
    @commands.has_role(ROLE_PERM)
    async def add_fragment(self, ctx, card, n):
        command = f'```{COMMAND_PREFIX}add [card name/ID] [quantity] @user```'
        session = Session()

        # Verify that card exists and get Card.id
        my_card = await get_card(session, ctx, card, command)
        if my_card is False:
            session.rollback()
            return

        # Verify that a user was mentioned
        mentioned_user = await verify_mentioned(ctx, command)
        if mentioned_user is False:
            session.rollback()
            return

        if n.isdigit():
            n = int(n)
            if 0 < n < 30:
                my_user = get_user(session, str(mentioned_user.id))
                my_user.add_to_deck(session, my_card.id, n)
                session.commit()
                await ctx.send(f'Added {n} **{my_card.title}** fragments to <@{str(mentioned_user.id)}>.')
                return
        session.rollback()
        await ctx.send(f'Quantity must be between 1 and 30\n{command}')

    @commands.command(aliases=['removefragment', 'REMOVEFRAGMENT', 'remove', 'REMOVE', 'rem', 'REM'])
    @commands.has_role(ROLE_PERM)
    async def remove_fragment(self, ctx, card, n):
        command = f'```{COMMAND_PREFIX}rem [card name/ID] [quantity] @user```'
        session = Session()

        # Verify that card exists and get Card.id
        my_card = await get_card(session, ctx, card, command)
        if my_card is False:
            session.rollback()
            return

        # Verify that a user was mentioned
        mentioned_user = await verify_mentioned(ctx, command)
        if mentioned_user is False:
            session.rollback()
            return

        if n.isdigit():
            n = int(n)
            if n > 0:
                my_user = get_user(session, str(mentioned_user.id))
                if n > my_user.get_quantity(session, my_card.id):
                    await ctx.send(f'{mentioned_user.display_name} does not have {n}x **{my_card.title}**.')
                    session.rollback()
                    return
                else:
                    await ctx.send(f'Removed {n}x **{my_card.title}** fragments from {mentioned_user.display_name}.')
                    my_user.remove_from_deck(session, my_card.id, n)
                    session.commit()
                    return
        await ctx.send(f'Quantity must be greater than 0.\n{command}')
        session.rollback()

    @commands.command(aliases=['setlevel', 'level', 'lvl', 'LVL'])
    @commands.has_role(ROLE_PERM)
    async def set_level(self, ctx, card, lvl):
        command = f'```{COMMAND_PREFIX}rem [card name/ID] [quantity] @user```'
        session = Session()

        my_card = await get_card(session, ctx, card, command)
        if my_card is False:
            session.rollback()
            return

        mentioned_user = await verify_mentioned(ctx, command)
        if mentioned_user is False:
            session.rollback()
            return

        if lvl.isdigit():
            lvl = int(lvl)
            if 0 <= lvl < 7:
                my_user = get_user(session, str(mentioned_user.id))
                my_user.set_level(session, my_card.id, lvl)
                session.commit()
                await ctx.send(f'Set {mentioned_user.display_name}\'s **{my_card.title}** to level {lvl}.')
                return
        session.rollback()
        await ctx.send(f'Level must be between 0 and 7.')

    @commands.command(aliases=['UPGRADE', 'u', 'U', 'up', 'UP'])
    async def upgrade(self, ctx, card):
        command = f'```{COMMAND_PREFIX}up [card name/ID]```'
        session = Session()

        my_card = await get_card(session, ctx, card, command)
        if my_card is False:
            session.rollback()
            return

        my_user = get_user(session, str(ctx.author.id))
        lvl = my_user.get_level(session, my_card.id)
        n = my_user.get_quantity(session, my_card.id)
        if n < lvl + 1:
            session.rollback()
            await ctx.send(f"{ctx.author.display_name} needs {lvl + 1} fragments to upgrade **{my_card.title}**, has {n}.")
        else:
            my_user.remove_from_deck(session, my_card.id, lvl + 1)
            my_user.set_level(session, my_card.id, lvl + 1)
            session.commit()
            file = discord.File(my_card.get_image_path(session, lvl + 1))
            await ctx.send(file=file)
            await ctx.send(f"{ctx.author.display_name} has upgraded their **{my_card.title}** to lvl {lvl + 1}!")

    @commands.command(aliases=['DESTROY'])
    async def destroy(self, ctx, card):
        command = f'```{COMMAND_PREFIX}destroy [card name/ID]```'
        session = Session()

        my_card = await get_card(session, ctx, card, command)
        if my_card is False:
            session.rollback()
            return

        my_user = get_user(session, str(ctx.author.id))

        level = my_user.get_level(session, my_card.id)
        buttons = [[Button(style=ButtonStyle.green, label='Accept'),
                    Button(style=ButtonStyle.red, label='Cancel')]]
        fragments = my_user.fragments_from_destroy(session, my_card.id)

        m = await ctx.send(f"Shatter your lvl {level} **{my_card.title}** into {fragments} fragments?",
                           components=buttons)

        def check(b):
            return b.author == ctx.author and b.channel == ctx.channel
        res = await self.bot.wait_for("button_click", check=check, timeout=180)
        await res.respond(type=6)
        res_text = res.component.label

        if res_text == 'Accept':
            await m.edit(components=[])
            my_user.set_level(session, my_card.id, 0)
            my_user.add_to_deck(session, my_card.id, fragments)
            session.commit()
            await ctx.send("Shattered.")
            return True
        elif res_text == 'Cancel':
            await m.edit(components=[])
            session.rollback()
            await ctx.send("Destruction canceled.")
            return False


def setup(bot):
    bot.add_cog(AdminEdit(bot))
