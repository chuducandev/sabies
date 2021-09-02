import discord
import os
import handlers
import utils
from keywords import commands
from discord.ext import tasks
from replit import database

discordToken = os.environ['DISCORD_TOKEN']
client = discord.Client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    message.content = ' '.join(message.content.split())

    # await message.channel.send(embed = utils.generateContent('<@!543776596834779171>'))
    # print(message.content)

    #get input
    input = message.content.split()

    if len(input) == 0:
        return

    if message.content.startswith('hello') or message.content.startswith('hi') or message.content.startswith('h'):
        await handlers.sayHello(message)

    if input[0] in commands['inspire']:
        await handlers.getQuote(message)

    if input[0] in commands['make']:
        if input[1] in commands['poll']:
            await handlers.makePoll(message, input)
        if input[1] in commands['meeting']:
            await handlers.makeMeeting(message, input)

    if input[0] in commands['edit']:
        if input[1] in commands['poll']:
            await handlers.editPoll(message, input)

@client.event
async def on_voice_state_update(member, before, after):
    await handlers.updateMeetingLastActive(before)

@client.event
async def on_raw_reaction_add(payload):
    if payload.member == client.user:
        return

    await handlers.updateMeetingAttendances(payload)

@tasks.loop(minutes = 1)
async def scheduler():
    await client.wait_until_ready()
    await handlers.cleanMeetings(client)
    await handlers.checkNotionMeetings(client)

scheduler.start()

client.run(discordToken)
