from discord.ext import commands
from source.db import Session
from source.verify import verify


class CollectionAdd(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def changeSet(self, ctx, card, quantity=1):
        session = Session()
        if not verify(session, ctx, card=card):
            # send message with command instructions
            return

        # retrieve card_id if card is a name
        # get @user from ctx
        # verify if user exists, if not create it
        # try/catch removing the fragments, send error message if user doesnt have enough
        # if fragments and level are both 0, delete card from user

        session.commit()
        session.close()



"""




"""

def setup(bot):
    bot.add_cog(CollectionAdd(bot))