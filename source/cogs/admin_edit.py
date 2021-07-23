from discord.ext import commands
from source.verify import verify
from source.db import Session

class AdminEdit(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    async def addFragment(self, ctx, card, quantity=1):
        session = Session()

        verify(session, ctx, card=card)



"""




"""

def setup(bot):
    bot.add_cog(AdminEdit(bot))
