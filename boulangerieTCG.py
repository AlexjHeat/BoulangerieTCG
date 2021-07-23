from discord.ext import commands
from source import config


client = commands.Bot(command_prefix=config.COMMAND_PREFIX)


@client.event
async def on_ready():
    print('Bot is online.')

client.run(config.DISCORD_TOKEN)
