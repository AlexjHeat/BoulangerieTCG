
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
    async def AddUserCard(self, ctx):
        session = Session()

        user = ctx.message.mentions[0]
        print(user)

        prefix = await set_input(self, session, ctx)
        my_set = session.query(Set).filter(Set.prefix == prefix).first()
        my_set.total_cards += 1

        card_id = my_set.prefix + str(my_set.total_cards)
        my_card = Card(id=card_id, prefix=prefix)

        if await populate_card(self, ctx, my_card, rarity=True, house=True, flavor=True) is False:
            session.rollback()
            return False

        # Grab the users information




        session.commit()
        session.close()

    @commands.command()
    async def AddCustomCard(self, ctx):
        session = Session()
        try:
            prefix = await set_input(self, session, ctx)
            my_set = session.query(Set).filter(Set.prefix == prefix).first()
            my_set.total_cards += 1

            card_id = my_set.prefix + str(my_set.total_cards)
            my_card = Card(id=card_id, prefix=prefix)

            if await populate_card(self, ctx, my_card,
                                   title=True, rarity=True, house=True, flavor=True, image=True) is False:
                session.rollback()
                return False

            session.add(my_card)
            for lvl in range(1, 8):
                session.add(CardLevel(card_id=my_card.id, level=lvl))

            my_stats = await stats_input(self, ctx, my_card.rarity)
            if my_stats is False:
                session.rollback()
                return False
            populate_stats(session, my_stats, my_card.id)

            if await accept_card(self, session, ctx, my_card) is False:
                session.rollback()
                return False

            for lvl in range(1, 8):
                if create_card(session, my_card, lvl) is False:
                    return False



        except asyncio.TimeoutError as e:
            session.rollback()
            print(type(e))
            print('edit_cards.AddCustomCard(): encountered Timeout error, function terminated')
            await ctx.send("Card creation: timed out")
            return False

        else:
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
    