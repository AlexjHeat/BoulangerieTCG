import discord
from discord.ext import commands
from source.db import Session
from source.config import PULLS_PER_DAY, COMMAND_PREFIX
from source.models.user import User
from source.models.set import Set


def roll(boost = None):
    # chance for rarity types kept in config
    # set can be boosted
    # days since legendary

    pass


async def pull_cards (ctx, user_id, checkPull=False, count=PULLS_PER_DAY):
    session = Session()

    # check if User object exists, and create one if not
    my_user = session.query(User).filter(User.id == user_id).one_or_none()
    if my_user is None:
        my_user = User(id=user_id, wins=0, losses=0, days_since_lgnd=0, pull_available=True, deck_private=False)
        session.add(my_user)

    # checks if user has a pull available if necessary
    if checkPull:
        if my_user.pull_available is False:
            await ctx.send(f'No pull available, resets at 0:00 GMT')
            return False
        my_user.pull_available = False

    # send a slot machine gif
    slot_file = discord.File('./media/images/slotmachine.gif')
    await ctx.send(file=slot_file)

    #

    # temp list = []
    # for _ in range(PULLS_PER_DAY)
    # send to algorithm function that returns a cardID at random
    # if card in temp_list
    # get new card (maybe make this a loop?
    # add card to temp list

    # for each card in temp_list
    # query for CardInstance(user, cardID)
    # if doesn't exist, create it and add to session
    # if does exist, update it

    # for each card in temp_list
    # Post each shard
    # Post name + rarity
    # if legendary, make special post or gif?
    session.rollback()




class Pull(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    async def pull(self, ctx):
        user_id = str(ctx.message.author.id)
        await pull_cards(ctx, user_id, checkPull=True)


    @commands.command()
    async def freePull(self, ctx, quantity):
        command = f"```{COMMAND_PREFIX}freePull [quantity] @user```"

        if not quantity.isdigit() or (int(quantity) < 0 or int(quantity) > 7):
            await ctx.send('Quantity must be between 0 and 7.\n' + command)
            return

        if len(ctx.message.mentions) != 1:
            await ctx.send('Need to @ a user.' + command)
            return

        user_id = str(ctx.message.mentions[0].id)
        await pull_cards(ctx, user_id, checkPull=False, count=quantity)



def setup(bot):
    bot.add_cog(Pull(bot))
