import discord
import CalendarSetup
from discord.ext import commands
print('Starting bot...')

TOKEN = open('BotToken.txt', 'r').readline()
bot = commands.Bot(command_prefix='!')


@bot.command()
async def ping(ctx):
    await ctx.send(f'Pong! {round (bot.latency * 1000)}ms')


@bot.command()
async def link(ctx):
    await ctx.send('Linking account')
    service = CalendarSetup.get_calendar_service()
    await ctx.send('Account linked')
    calendar_id = get_calendar_id(service)
    if(calendar_id == None):
        calendar = {
            'summary': 'Due Dates',
            'timeZone': 'Canada/Pacific'
        }
        created_calendar = service.calendars().insert(body=calendar).execute()
        calendarId = created_calendar['id']
        await ctx.send('Due Dates calendar created')
    else:
        await ctx.send('Due Dates calendar found')


@bot.command()
async def list(ctx):
    service = CalendarSetup.get_calendar_service()


@bot.command()
async def create(ctx, msg):
    service = CalendarSetup.get_calendar_service()
    calendar_id = get_calendar_id(service)

    calendar = service.calendars().get(calendarId=calendar_id).execute()

    print(calendar['summary'])
    event = {
        'summary': 'Google I/O 2015',
        'location': '800 Howard St., San Francisco, CA 94103',
        'description': 'A chance to hear more about Google\'s developer products.',
        'start': {
            'dateTime': '2020-12-02T09:00:00-07:00',
            'timeZone': 'America/Los_Angeles',
        },
        'end': {
            'dateTime': '2020-12-02T17:00:00-07:00',
            'timeZone': 'America/Los_Angeles',
        },
    }

    event = service.events().insert(calendarId=calendar_id, body=event).execute()
    await ctx.send('Event created: %s' % (event.get('htmlLink')))


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
        name='!link', value='''Authorize the bot to access your google calendar.
                            All event created will be on a calendar called "Due Dates"''', inline=False)
    embed.add_field(
        name='!ping', value='Returns bot respond time in milliseconds', inline=False)
    await ctx.send(embed=embed)


def get_calendar_id(service):
    page_token = None
    cal_not_found = True
    while cal_not_found:
        calendar_list = service.calendarList().list(pageToken=page_token).execute()
        for calendar_list_entry in calendar_list['items']:
            if(calendar_list_entry['summary'] == 'Due Dates'):
                return calendar_list_entry['id']
        page_token = calendar_list.get('nextPageToken')
        if not page_token:
            break
    return None


print("Bot is ready!")
bot.run(TOKEN)