import sqlalchemy.exc
from discord.ext import commands
from sqlalchemy import exc
from source.db import Session
from source.stats import populate_stats
from source.image import create_image
from source.input import *
from source.verify import verify_card
from source.models.card import Card
from source.models.set import Set
from source.models.card_level import CardLevel


# TODO: enable .gif cards by parsing file extension on input, maybe just for level 5+
async def create_card(self, session, ctx, my_card):
    try:
        session.add(my_card)

        # Add the bare 7 CardLevel objects
        for lvl in range(1, 8):
            session.add(CardLevel(card_id=my_card.id, level=lvl))

        # Generate stats for each level and add them to the CardLevel objects
        my_stats = await stats_input(self, ctx, my_card.rarity.name)
        populate_stats(session, my_stats, my_card.id)

        # Give the user the opportunity to edit or cancel the card
        if await accept_card(self, session, ctx, my_card) is False:
            session.rollback()
            return

        # Create card images (.png) for each of the 7 levels
        for lvl in range(1, 8):
            if create_image(session, my_card, lvl) is False:
                await ctx.send("Error encountered with card image creation, command terminated")
                session.rollback()
                return False

    except asyncio.TimeoutError as e:
        session.rollback()
        print(type(e))
        print('edit_cards.create_card(): encountered Timeout error, function terminated')
        await ctx.send("Card creation: timed out")
        return False
    else:
        # If there were no exceptions, then the session is finally committed and a confirmation message sent
        q_level = session.query(CardLevel).filter(CardLevel.card_id == my_card.id, CardLevel.level == 1).one_or_none()
        file = discord.File(q_level.artPath)
        await ctx.send(file=file)
        await ctx.send(f'**{my_card.title}** has been created!')
        session.commit()


class EditCards(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['usercard', 'ucard'])
    @commands.max_concurrency(1)
    @commands.has_role(ROLE_PERM)
    async def UserCard(self, ctx):
        command = f"```{COMMAND_PREFIX}AddUser @user```"
        session = Session()

        # Ensures that a user was mentioned in the command and gets it
        if len(ctx.message.mentions) == 0:
            await ctx.send('No user mentioned.\n' + command)
            return
        user = ctx.message.mentions[0]

        try:
            # Gets the set information for the id, and creates the Card object
            prefix = await set_input(self, session, ctx)
            my_set = session.query(Set).filter(Set.prefix == prefix).one_or_none()
            my_set.total_cards += 1

            card_id = my_set.prefix + str(my_set.total_cards)
            my_card = Card(id=card_id, prefix=prefix)

            # Gets the username and pfp to add to the Card object
            title = user.nick
            if title is None:
                title = user.name
            my_card.title = title[:MAX_TITLE_LENGTH]

            filename = './media/card_art/' + my_card.id + '_art.png'
            await user.avatar_url.save(filename)
            my_card.artPath = filename

            # Gets input for the rest of the Card object
            await populate_card(self, ctx, my_card, rarity=True, house=True, flavor=True)

            # Now that the card has all the inputs, send it to create_card()
            if await create_card(self, session, ctx, my_card) is False:
                return

        except asyncio.TimeoutError as e:
            session.rollback()
            print(type(e))
            print('edit_cards.AddUser(): encountered Timeout error, function terminated')
            await ctx.send("Card creation: timed out")
            return False


    @commands.command(aliases=['customcard', 'ccard'])
    @commands.max_concurrency(1)
    @commands.has_role(ROLE_PERM)
    async def CustomCard(self, ctx):
        session = Session()
        try:
            # Gets the set information for the id, and creates the Card object
            prefix = await set_input(self, session, ctx)
            my_set = session.query(Set).filter(Set.prefix == prefix).one_or_none()
            my_set.total_cards += 1

            card_id = my_set.prefix + str(my_set.total_cards)
            my_card = Card(id=card_id, prefix=prefix)

            # Gets input for the rest of the Card object
            await populate_card(self, ctx, my_card, title=True, rarity=True, house=True, flavor=True, image=True)

            # Send to
            await create_card(self, session, ctx, my_card)

        except asyncio.TimeoutError as e:
            session.rollback()
            print(type(e))
            print('edit_cards.AddCustom(): encountered Timeout error, function terminated')
            await ctx.send("Card creation: timed out")
            return



    @commands.command()
    async def RemoveCard(self, ctx, card):
        command = f"```{COMMAND_PREFIX}RemoveCard [card ID/title]```"
        session = Session()

        # Verify that the command argument is correct, and get the proper card_id string
        card_id = verify_card(session, card)
        if card_id is False:
            await ctx.send(f'CARD ERROR: **{card}** does not exist.\n{command}')
            return

        # TODO: Implement RemoveCard command
        # Delete it such that it cascades and removes all associated CardLevel and CardInstance objects
        # Some sort of confirmation, extra security, to prevent deleting the card on accident
            # send a random code that must be copied and messaged back
            # make user reply 'yes' in DMs

        session.commit()
        session.close()

    @commands.command(aliases=['editcard', 'edit'])
    @commands.max_concurrency(1)
    @commands.has_role(ROLE_PERM)
    async def EditCard(self, ctx, card):
        command = f"```{COMMAND_PREFIX}EditCard [card ID/title]```"
        session = Session()

        # Verify that the command argument is correct, and get the proper card_id string
        card_id = verify_card(session, card)
        if card_id is False:
            await ctx.send(f'CARD ERROR: **{card}** does not exist.\n{command}')
            return
        # Retrieve Card object
        my_card = session.query(Card).filter(Card.id == card_id).one()

        # Give the user the accept_card() menu to cancel, make edits, and accept the edits
        if await accept_card(self, session, ctx, my_card) is False:
            session.rollback()
            return

        # Recreate card images (.png) for each of the 7 levels
        for lvl in range(1, 8):
            if create_image(session, my_card, lvl) is False:
                await ctx.send("Error encountered with card image creation, command terminated")
                session.rollback()
                return

        session.commit()
        q_level = session.query(CardLevel).filter(CardLevel.card_id == my_card.id, CardLevel.level == 1).one_or_none()
        file = discord.File(q_level.artPath)
        await ctx.send(file=file)
        await ctx.send(f'**{my_card.title}** has been edited.')


def setup(bot):
    bot.add_cog(EditCards(bot))
