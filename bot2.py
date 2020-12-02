import discord
from discord.ext import commands

client = commands.Bot(command_prefix = '.')

@client.event
async def on_ready():
    print('Bot is ready to go .')
client.run('NzgwNTU2MTQ0NDgxMDA5NzE0.X7wzjg.b86VdPQ7mTWJ5dZm8MhOAim5Ic0')
