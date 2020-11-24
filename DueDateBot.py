import discord
from discord.ext import commands
print('Starting bot...')

TOKEN = open('BotToken.txt', 'r').readline()
bot = commands.Bot(command_prefix='!')

@bot.command()
async def ping(ctx):
    await ctx.send(f'Pong! {round (bot.latency * 1000)}ms')

@bot.command()
async def create(ctx, msg):
    await ctx.send(msg)

@bot.event
async def on_command_error(ctx, error):
    await ctx.send(f'{error}\nTry !help')

# We delete default help command
bot.remove_command('help')
# Embeded help with list and details of commands
@bot.command(pass_context=True)
async def help(ctx):
    embed = discord.Embed(colour=discord.Colour.green())
    embed.set_author(name='Help : list of commands available')
    embed.add_field(
        name='.ping', value='Returns bot respond time in milliseconds', inline=False)
    await ctx.send(embed=embed)

print("Bot is ready!")
bot.run(TOKEN)