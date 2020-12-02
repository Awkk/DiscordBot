import discord
import CalendarSetup
import datetime
import dateparser
import json
from discord.ext import commands
from dateutil.parser import parse as dtparse
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
        with open('setting.json') as f:
            timezone = json.load(f)['timezone']
        calendar = {
            'summary': 'Due Dates',
            'timeZone': timezone
        }
        created_calendar = service.calendars().insert(body=calendar).execute()
        calendarId = created_calendar['id']
        await ctx.send('Due Dates calendar created')
    else:
        await ctx.send('Due Dates calendar found')


# list command
@bot.command()
async def list(ctx):
    service = CalendarSetup.get_calendar_service()
    calendar_id = get_calendar_id(service)
    page_token = None
    current_date = datetime.datetime.now()
    active = []
    while True:
        events = service.events().list(calendarId=calendar_id,
                                       pageToken=page_token).execute()
        for event in events['items']:
            due_date = dtparse(event['start']['dateTime']).replace(tzinfo=None)
            if(due_date > current_date):
                active.append((due_date, event['summary']))

        page_token = events.get('nextPageToken')
        if not page_token:
            break

    active.sort()
    embed = discord.Embed(title='All Due Dates', colour=discord.Colour.red())
    for event in active:
        embed.add_field(name=event[1], value=event[0].strftime('%d-%b-%y %a %I:%M%p'), inline=False)

    await ctx.send(embed=embed)


# create command
@bot.command()
async def create(ctx, *, msg):
    service = CalendarSetup.get_calendar_service()
    calendar_id = get_calendar_id(service)
    calendar = service.calendars().get(calendarId=calendar_id).execute()
    with open('setting.json') as f:
        timezone = json.load(f)['timezone']

    info = msg.split(',', 1)
    title = info[0]
    date = dateparser.parse(info[1]).isoformat('T')

    event = {
        'summary': title,
        'start': {
            'dateTime': date,
            'timeZone': 'Canada/Pacific',
        },
        'end': {
            'dateTime': date,
            'timeZone': 'Canada/Pacific',
        },
    }

    event = service.events().insert(calendarId=calendar_id, body=event).execute()
    await ctx.send('Event created: %s' % (event.get('htmlLink')))


@bot.command()
async def delete(ctx, *, msg):
    service = CalendarSetup.get_calendar_service()
    calendar_id = get_calendar_id(service)
    page_token = None
    while True:
        events = service.events().list(calendarId=calendar_id,
                                       pageToken=page_token).execute()
        for event in events['items']:
            if(event['summary'] == msg):
                service.events().delete(calendarId=calendar_id,
                                        eventId=event['id']).execute()
                await ctx.send('Deleted ' + msg)
                return

        page_token = events.get('nextPageToken')
        if not page_token:
            break
    await ctx.send(msg + ' not found')


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
        name='!ping', value='Returns bot response time in milliseconds', inline=False)
    embed.add_field(
        name='!create', value='''Creates an event in Google Calendar. 
                            Ex) !create eventname, YYYY MMM 3 10:00pm, ''', inline=False)
    embed.add_field(
        name='!delete', value='''Deletes an event in Google Calendar. 
                            Ex) !delete id''', inline=False)
    embed.add_field(
        name='!update', value='''Updates an event to a different time/date.
                            Ex)!update id ''', inline=False)
    embed.add_field(
        name='!day', value='''Returns all events today. 
                            Ex)!day ''', inline=False)
    embed.add_field(
        name='!week', value='''Return all events this week.
                            Ex)!week ''', inline=False)
    embed.add_field(
        name='!month', value='''Return all events this month.
                            Ex)!month ''', inline=False)

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
