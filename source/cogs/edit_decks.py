from discord.ext import commands
from source.verify import verify_card
from source.db import Session

class AdminEdit(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    async def AddFragment(self, ctx, card, quantity=1):
        session = Session()
        card = await verify_card(session, ctx, card)
        if not card:
            await ctx.send("Command format: (do not include brackets)```.AddFragment [card name/ID] [quantity]```")
            session.close()
            return False

        # get @user from ctx
        # verify if user exists, if not create it
        # add fragments to user (maybe a User class function)

        session.commit()
        session.close()


    @commands.command()
    async def RemoveFragment(self, ctx, card, quantity=1):
        session = Session()
        card = await verify_card(session, ctx, card)
        if not card:
            await ctx.send("Command format: (do not include brackets)```.RemoveFragment [card name/ID] [quantity]```")
            session.close()
            return False

        # retrieve card_id if card is a name
        # get @user from ctx
        # verify if user exists, if not create it
        # try/catch removing the fragments, send error message if user doesnt have enough
        # if fragments and level are both 0, delete card from user

        session.commit()
        session.close()


    @commands.command()
    async def SetLevel(self, ctx, card, level):
        session = Session()
        card = await verify_card(session, ctx, card)
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
