import asyncio
import discord
from discord_components import *
from source.config import *
from source.stats import populate_stats
from source.models.set import Set
from source.models.card import RarityEnum, HouseEnum
from source.models.card_level import CardLevel


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
        color=COLOR_HEX[my_card.house]
    )
    my_set = session.query(Set).filter(Set.prefix == my_card.prefix).first()
    embed.set_thumbnail(url='attachment://image.png')
    embed.add_field(name='Card Title', value=my_card.title, inline=False)
    embed.add_field(name='Set', value=my_set.name, inline=False)
    embed.add_field(name='House', value=my_card.house, inline=True)
    embed.add_field(name='Rarity', value=my_card.rarity, inline=True)

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
                embed.insert_field_at(2, name="House", value=my_card.house, inline=True)

            elif res_text == 'Flavor':
                my_card.flavor = await flavor_input(self, ctx)
                embed.remove_field(5)
                embed.insert_field_at(5, name="Flavor text", value=my_card.flavor, inline=True)

            elif res_text == 'Stats':
                stats = await stats_input(self, ctx, my_card.rarity)
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


# Checks if user input is in a list
async def check_list(self, ctx, lst):
    def check(m):
        if m.author == ctx.author and m.channel == ctx.channel:
            if m.content.upper() in lst:
                return True
        return False

    message = await self.bot.wait_for('message', check=check, timeout=60)
    return message.content.upper()


# Checks if user input is below a maximum length
async def check_length(self, ctx, max_len):
    def check(m):
        if m.author == ctx.author and m.channel == ctx.channel:
            if len(m.content) < max_len:
                return True
        return False

    message = await self.bot.wait_for('message', check=check, timeout=60)
    return message.content


async def check_author(self, ctx):
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        message = await self.bot.wait_for('message', check=check, timeout=60)
    except asyncio.TimeoutError:
        await ctx.send('Card creation: timed out')
        return False
    return message


async def title_input(self, ctx):
    await ctx.send(f'Enter the card title ({MAX_TITLE_LENGTH} character limit): ')
    return await check_length(self, ctx, MAX_TITLE_LENGTH)


async def set_input(self, session, ctx):
    set_list = [item.prefix for item in session.query(Set)]
    await ctx.send(f'Enter one of the following set prefixes {set_list}:')
    return await check_list(self, ctx, set_list)


async def rarity_input(self, ctx):
    rarity_list = [item.value for item in RarityEnum]
    await ctx.send(f'Enter one of the following rarities {rarity_list}:')
    rarity = await check_list(self, ctx, rarity_list)
    return RarityEnum(rarity).name


async def house_input(self, ctx):
    house_list = [item.value for item in HouseEnum]
    await ctx.send(f'Enter one of the following houses {house_list}:')
    house = await check_list(self, ctx, house_list)
    return HouseEnum(house).name


async def flavor_input(self, ctx):
    await ctx.send(f'Enter the flavor text:')
    message = await check_author(self, ctx)
    return message.content
# TODO: add a proper check to the flavor to keep it in the box


async def stats_input(self, ctx, rarity):
    rarity_list = [item.name for item in RarityEnum]
    i = rarity_list.index(rarity)
    await ctx.send(f'Enter stats in the form **[post lurk react]**\n'
                   f'Total between **{MIN_STATS[i]}** and **{MAX_STATS[i]}**:')

    while True:
        message = await check_author(self, ctx)
        if message is False:
            return False

        stats = message.content.split()
        stats_int = [int(x) for x in stats if x.isdigit()]
        if len(stats_int) == len(rarity_list):
            if sum(stats_int) <= MAX_STATS[i] and sum(stats_int) >= MIN_STATS[i]:
                return stats_int


async def image_input(self, ctx):
    await ctx.send('Upload an image:')

    image_valid = False
    while not image_valid:
        message = await check_author(self, ctx)
        if message is False:
            return False

        if len(message.attachments) == 1:
            if 'image' in message.attachments[0].content_type:
                image_valid = True
    return message.attachments[0]


async def populate_card(self, ctx, my_card, title=False, rarity=False, house=False, flavor=False, image=False):
    if title:
        my_card.title = await title_input(self, ctx)

    if rarity:
        my_card.rarity = await rarity_input(self, ctx)

    if house:
        my_card.house = await house_input(self, ctx)

    if flavor:
        my_card.flavor = await flavor_input(self, ctx)

    if image:
        image = await image_input(self, ctx)
        filename = './media/card_art/' + my_card.id + '_art.png'
        await image.save(filename)
        my_card.artPath = filename
    return True
