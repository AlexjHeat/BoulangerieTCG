from .config import MAX_TITLE_LENGTH, MIN_STATS, MAX_STATS
from .models.set import Set
from .models.card import RarityEnum, HouseEnum


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
    message = await self.bot.wait_for('message', check=check, timeout=60)
    return message


async def title_input(self, ctx):
    await ctx.send(f'Enter the card title ({MAX_TITLE_LENGTH} character limit): ')
    return await check_length(self, ctx, MAX_TITLE_LENGTH)


async def set_input(self, session, ctx):
    set_list = [item.prefix for item in session.query(Set)]
    await ctx.send(f'Enter one of the following set prefixes {set_list}:')
    return await check_list(self, ctx, set_list)


async def rarity_input(self, ctx):
    rarity_list_key = [f'{item.value}' for item in RarityEnum]
    rarity_list = [f'{item.value}: {item.name}' for item in RarityEnum]
    await ctx.send(f"Enter one of the following rarity numbers\n{rarity_list}:")
    rarity = int(await check_list(self, ctx, rarity_list_key))
    return RarityEnum(rarity)


async def house_input(self, ctx):
    house_list_key= [f'{item.value}' for item in HouseEnum]
    house_list = [f'{item.value}: {item.name}' for item in HouseEnum]
    await ctx.send(f"Enter a house's corresponding number {house_list}:")
    house = int(await check_list(self, ctx, house_list_key))
    return HouseEnum(house)


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
    return
