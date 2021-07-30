import sqlalchemy.exc
from discord.ext import commands
from sqlalchemy import exc
from source.db import Session
from source.stats import populate_stats
from source.image import create_card
from source.input import *
from source.verify import verify_card
from source.models.card import Card
from source.models.set import Set
from source.models.card_level import CardLevel





class CollectionAdd(commands.Cog):
    def __init__(self, bot):
        self.bot = bot



    @commands.command()
    async def AddUser(self, ctx):
        command = f"```{COMMAND_PREFIX}AddUser @user```"
        session = Session()

        try:
            # Ensures that a user was mentioned in the command and gets it
            if len(ctx.message.mentions) == 0:
                await ctx.send('No user mentioned.\n' + command)
                return
            user = ctx.message.mentions[0]

            # Gets the set information for the id, and creates the Card object
            prefix = await set_input(self, session, ctx)
            my_set = session.query(Set).filter(Set.prefix == prefix).first()
            my_set.total_cards += 1

            card_id = my_set.prefix + str(my_set.total_cards)
            my_card = Card(id=card_id, prefix=prefix)

            title = user.nick
            if title is None:
                title = user.name
            my_card.title = title[:MAX_TITLE_LENGTH]

            filename = './media/card_art/' + my_card.id + '_art.png'
            await user.avatar_url.save(filename)
            my_card.artPath = filename

            await populate_card(self, ctx, my_card, rarity=True, house=True, flavor=True)



        except asyncio.TimeoutError as e:
            session.rollback()
            print(type(e))
            print('edit_cards.AddUser(): encountered Timeout error, function terminated')
            await ctx.send("Card creation: timed out")
            return False





        session.rollback()
        session.close()

    @commands.command()
    async def AddCustom(self, ctx):
        session = Session()
        try:
            prefix = await set_input(self, session, ctx)
            my_set = session.query(Set).filter(Set.prefix == prefix).first()
            my_set.total_cards += 1

            card_id = my_set.prefix + str(my_set.total_cards)
            my_card = Card(id=card_id, prefix=prefix)

            await populate_card(self, ctx, my_card, title=True, rarity=True, house=True, flavor=True, image=True)

            session.add(my_card)
            for lvl in range(1, 8):
                session.add(CardLevel(card_id=my_card.id, level=lvl))

            my_stats = await stats_input(self, ctx, my_card.rarity.name)
            populate_stats(session, my_stats, my_card.id)

            if await accept_card(self, session, ctx, my_card) is False:
                session.rollback()
                return

            for lvl in range(1, 8):
                if create_card(session, my_card, lvl) is False:
                    await ctx.send("Error encountered with card image creation, command terminated")
                    session.rollback()
                    return

        except exc.SQLAlchemyError as e:
            print(type(e))
            print('edit_cards.AddCustom(): database error, command terminated')
            await ctx.send("Error encountered with database, command terminated")

        except asyncio.TimeoutError as e:
            session.rollback()
            print(type(e))
            print('edit_cards.AddCustom(): encountered Timeout error, function terminated')
            await ctx.send("Card creation: timed out")
            return
        else:
            await ctx.send(f'**{my_card.title}** has been created!')
            session.commit()



    @commands.command()
    async def RemoveCard(self, ctx):
        session = Session()

       # if not verify(session, ctx, set=old_prefix):
            # send message with command instructions
           # return False
        # verify_set function to verify new_prefix(4) and setName length
        # Add set to database

        session.commit()
        session.close()


    @commands.command()
    async def EditCard(self, ctx, card_id):
        session = Session()

        card_id = verify_card(session, ctx, card_id)
        if card_id is False:
            return False

        session.commit()
        session.close()


def setup(bot):
    bot.add_cog(CollectionAdd(bot))
    