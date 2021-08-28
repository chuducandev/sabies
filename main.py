import discord
import os
import handlers
from replit import database

discordToken = os.environ['DISCORD_TOKEN']
client = discord.Client()



@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    message.content = ' '.join(message.content.split())

    if message.author == client.user:
        return

    if message.content.startswith('-hello'):
        await handlers.sayHello(message)

    if message.content.startswith('-inspire'):
        await handlers.getQuote(message)

    if message.content.startswith('-make poll'):
        await handlers.makePoll(message)

    if message.content.startswith('-make meeting'):
        await handlers.makeMeeting(message)

    if message.content.startswith('-edit poll'):
        await handlers.editPoll(message)

client.run(discordToken)
