from discord.ext import commands
from source.db import Session


class CollectionEdit(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def AddSet(self, ctx, prefix, setName):
        session = Session()
        #verify_new_set function to verify prefix(4) and setName length
        #Add set to database

        session.commit()
        session.close()

    @commands.command()
    async def EditSet(self, ctx, old_prefix, new_prefix, setName):
        session = Session()
        #if not verify(session, ctx, set=old_prefix):
            # send message with command instructions
            #return False
        # verify_new_set function to verify new_prefix(4) and setName length
        # Add set to database

        session.commit()
        session.close()

def setup(bot):
    bot.add_cog(CollectionEdit(bot))