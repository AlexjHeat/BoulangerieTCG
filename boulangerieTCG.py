import os
from discord.ext import commands
from source import config
from discord_components import *


bot = commands.Bot(command_prefix=config.COMMAND_PREFIX)


@bot.event
async def on_ready():
    DiscordComponents(bot)
    print('Bot is online.')


@bot.command()
async def load(ctx, extension):
    bot.load_extension(f'cogs.{extension}')


@bot.command()
async def unload(ctx, extension):
    bot.unload_extension(f'cogs.{extension}')


for filename in os.listdir('./source/cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'source.cogs.{filename[:-3]}')

bot.run(config.DISCORD_TOKEN)
