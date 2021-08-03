import discord
from discord.ext import commands
from discord_components import *
from source.db import Session
from source.config import COLOR_HEX, ROLE_PERM, COMMAND_PREFIX
from source.stats import populate_stats
from source.image import create_image
from source.input import *
from source.verify import verify_card, verify_mentioned
from source.models.card import Card
from source.models.set import Set
from source.models.card_level import CardLevel
import asyncio


async def get_button_response(self, ctx):
    def check(b):
        return b.author == ctx.author and b.channel == ctx.channel

    button = await self.bot.wait_for("button_click", check=check, timeout=180)
    return button


async def accept_card(self, session, ctx, my_card):

    buttons_approve = [[Button(style=ButtonStyle.green, label="Accept"),
                        Button(style=ButtonStyle.blue, label="Edit"),
                        Button(style=ButtonStyle.red, label="Cancel")]]
    buttons_edit = [[Button(style=ButtonStyle.blue, label="Title"),
                     Button(style=ButtonStyle.blue, label="House"),
                     Button(style=ButtonStyle.blue, label="Flavor")],
                    [Button(style=ButtonStyle.blue, label="Stats"),
                     Button(style=ButtonStyle.blue, label="Art")]]

    embed = discord.Embed(
        title=my_card.id,
        color=COLOR_HEX[my_card.house.name]
    )
    my_set = session.query(Set).filter(Set.prefix == my_card.prefix).first()
    embed.set_thumbnail(url='attachment://image.png')
    embed.add_field(name='Card Title', value=my_card.title, inline=False)
    embed.add_field(name='Set', value=my_set.name, inline=False)
    embed.add_field(name='House', value=my_card.house.name, inline=True)
    embed.add_field(name='Rarity', value=my_card.rarity.name, inline=True)

    stats = session.query(CardLevel).filter(CardLevel.card_id == my_card.id).first()
    embed.add_field(name='Post - Lurk - React',
                    value=str(stats.post) + " - " + str(stats.lurk) + " - " + str(stats.react), inline=False)
    embed.add_field(name='Flavor text', value=my_card.flavor, inline=False)

    while True:
        try:
            file = discord.File(my_card.artPath, filename='image.png')
        except FileNotFoundError as e:
            print(type(e))
            print('input.accept_card(): ' + my_card.artPath + ' cannot be found.')
            await ctx.send(my_card.artPath + ' cannot be found.')
            return False

        m = await ctx.send(file=file,
                           embed=embed,
                           components=buttons_approve)

        res = await get_button_response(self, ctx)
        await res.respond(type=6)
        res_text = res.component.label

        if res_text == 'Accept':
            await m.edit(components=[])
            return True
        elif res_text == 'Cancel':
            await m.edit(components=[])
            return False

        await m.edit(components=buttons_edit)
        res = await get_button_response(self, ctx)
        await res.respond(type=6)
        res_text = res.component.label

        try:
            if res_text == 'Title':
                my_card.title = await title_input(self, ctx)
                embed.remove_field(0)
                embed.insert_field_at(0, name="Card Title", value=my_card.title, inline=False)

            elif res_text == 'House':
                my_card.house = await house_input(self, ctx)
                embed.remove_field(2)
                embed.insert_field_at(2, name="House", value=my_card.house.name, inline=True)

            elif res_text == 'Flavor':
                my_card.flavor = await flavor_input(self, ctx)
                embed.remove_field(5)
                embed.insert_field_at(5, name="Flavor text", value=my_card.flavor, inline=True)

            elif res_text == 'Stats':
                stats = await stats_input(self, ctx, my_card.rarity.name)
                populate_stats(session, stats, my_card.id)
                stats = session.query(CardLevel).filter(CardLevel.card_id == my_card.id, CardLevel.level == 1).first()
                embed.remove_field(4)
                embed.insert_field_at(4, name='Post - Lurk - React',
                                      value=str(stats.post) + " - " + str(stats.lurk) + " - " + str(stats.react),
                                      inline=False)

            elif res_text == 'Art':
                image = await image_input(self, ctx)
                filename = './media/card_art/' + my_card.id + '_art.png'
                await image.save(filename)

        except asyncio.TimeoutError as e:
            print(e)
            print('input.accept_card() editing timed out')
        await m.delete()


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

    @commands.command(name='UserCard', aliases=['usercard', 'user', 'USERCARD'])
    @commands.max_concurrency(1)
    @commands.has_role(ROLE_PERM)
    async def user_card(self, ctx):
        command = f"```{COMMAND_PREFIX}user @user```"
        session = Session()

        # Ensures that a user was mentioned in the command and gets it
        user = await verify_mentioned(ctx, command=command)
        if user is None:
            session.rollback
            return False

        try:
            # Gets the set information for the id, and creates the Card object
            prefix = await set_input(self, session, ctx)
            my_set = session.query(Set).filter(Set.prefix == prefix).one_or_none()
            my_set.total_cards += 1

            card_id = my_set.prefix + str(my_set.total_cards)
            my_card = Card(id=card_id, prefix=prefix)

            # Gets the username and pfp to add to the Card object
            print(user.nick)
            my_card.title = user.display_name[:MAX_TITLE_LENGTH]

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


    @commands.command(name= 'CustomCard', aliases=['customcard', 'custom', 'CUSTOMCARD'])
    @commands.max_concurrency(1)
    @commands.has_role(ROLE_PERM)
    async def custom_card(self, ctx):
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

    @commands.command(name='RemoveCard', aliases=['removecard', 'REMOVECARD'])
    @commands.has_role(ROLE_PERM)
    async def remove_card(self, ctx, card):
        command = f"```{COMMAND_PREFIX}RemoveCard [card ID/title]```"
        session = Session()

        # Verify that the command argument is correct, and get the proper card_id string
        my_card = await verify_card(session, card)
        if my_card is False:
            session.rollback()
            return

        # TODO: Implement RemoveCard command
        # Delete it such that it cascades and removes all associated CardLevel and CardInstance objects
        # Some sort of confirmation, extra security, to prevent deleting the card on accident
            # send a random code that must be copied and messaged back
            # make user reply 'yes' in DMs

        session.commit()
        session.close()

    @commands.command(name='EditCard', aliases=['editcard', 'edit', 'EDITCARD'])
    @commands.max_concurrency(1)
    @commands.has_role(ROLE_PERM)
    async def edit_card(self, ctx, card):
        command = f"```{COMMAND_PREFIX}EditCard [card ID/title]```"
        session = Session()

        # Get the card
        my_card = await verify_card(session, ctx, card, command)
        if my_card is False:
            session.rollback()
            return

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
