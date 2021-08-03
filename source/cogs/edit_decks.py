from discord.ext import commands
from source.verify import verify_card, verify_mentioned, get_user
from source.db import Session
from source.config import COMMAND_PREFIX, ROLE_PERM

class AdminEdit(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='AddFragment', aliases=['addfragment', 'ADDFRAGMENT', 'ADD', 'add'])
    @commands.has_role(ROLE_PERM)
    async def add_fragment(self, ctx, card, n):
        command = f'```{COMMAND_PREFIX}add [card name/ID] [quantity] @user```'
        session = Session()

        # Verify that card exists and get Card.id
        my_card = await verify_card(session, ctx, card, command)
        if my_card is False:
            session.rollback()
            return
        mentioned_user = await verify_mentioned(ctx, command)
        if mentioned_user is False:
            session.rollback()
            return

        #Verify quantity
        if isinstance(n, str):
            await ctx.send(f'Quantity must be between 1 and 30\n{command}')
            return
        if n < 1 or n > 30:
            await ctx.send(f'Quantity must be between 1 and 30\n{command}')
            return

        my_user = get_user(session, str(mentioned_user.id))
        my_user.add_to_collection(session, my_card.id, n)
        await ctx.send(f'Added {n} **{my_card.title}** fragments to <@{str(mentioned_user.id)}>')
        session.commit()

    @commands.command(name='RemoveFragment', aliases=['removefragment', 'REMOVEFRAGMENT', 'rem', 'REM'])
    @commands.has_role(ROLE_PERM)
    async def remove_fragment(self, ctx, card, n):
        command = f'```{COMMAND_PREFIX}rem [card name/ID] [quantity] @user```'
        session = Session()

        # Verify that card exists and get Card.id
        my_card = await verify_card(session, ctx, card, command)
        if my_card is False:
            session.rollback()
            return
        mentioned_user = await verify_mentioned(ctx, command)
        if mentioned_user is False:
            session.rollback()
            return

        my_user = get_user()
        # verify if user exists, terminate with error message
        # try/catch removing the fragments, send error message if user doesnt have enough
        # if fragments and level are both 0, delete card from user

        session.commit()
        session.close()

    @commands.command()
    async def SetLevel(self, ctx, card, level):
        command = None
        session = Session()

        card = await verify_card(session, ctx, card, command)
        if not card:
            await ctx.send("Command format: (do not include brackets)```.SetLevel [card name/ID] [level]```")
            session.close()
            return False

        # retrieve card_id if card is a name
        # get @user from ctx
        # verify if user exists, if not create it
        # change the level
        # if fragments and level are both 0, delete card from user

        session.commit()
        session.close()

def setup(bot):
    bot.add_cog(AdminEdit(bot))
