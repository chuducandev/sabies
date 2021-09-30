import discord
import os
import handlers
import utils
from keywords import commands
from discord.ext import tasks
from replit import database

discordToken = os.environ['DISCORD_TOKEN']
intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents = intents)

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    await handlers.updateLastMessage(message)

    message.content = ' '.join(message.content.split())

    # await message.channel.send(embed = utils.generateContent('<@!543776596834779171>'))
    # print(message.content)

    #get input
    input = message.content.split()

    if len(input) == 0:
        return

    if input[0] in commands['hello']:
        await handlers.sayHello(message)

    if input[0] in commands['inspire'] and len(input) <= 1:
        await handlers.getQuote(message)

    if input[0] in commands['make']:
        if input[1] in commands['poll']:
            await handlers.makePoll(message, input)
        if input[1] in commands['meeting']:
            await handlers.makeMeeting(message, input)
        if input[1] in commands['random']:
            await handlers.makeRandom(message, input)
        if input[1] in commands['announcement']:
            await handlers.makeAnnouncement(message, input)

    if input[0] in commands['edit']:
        if input[1] in commands['poll']:
            await handlers.editPoll(message, input)
        if input[1] in commands['meeting']:
            await handlers.editMeeting(message, input)

    if input[0] in commands['delete']:
        if input[1] in commands['meeting']:
            await handlers.deleteMeeting(message, input)

    if input[0] in commands['help']:
        content = None
        defaultDescription = 'Keywords can be called with their first characters (Example: Use `e p 14 a Nevermind` instead of `edit poll 14 add Nevermind`).'
        if len(input) == 1:
            content = discord.Embed(
                title = 'Bot Documentation',
                colour = discord.Colour.green(),
                description = 'Follow the instruction below to find out each command\'s usage. ' + defaultDescription
            )

            utils.generateHelpContent(content, '')

        elif input[1]in commands['make']:
            content = discord.Embed(
                title = 'Bot Documentation',
                colour = discord.Colour.green(),
                description = defaultDescription,
            )
            
            if len(input) == 2:
                utils.generateHelpContent(content, 'make-meeting-complete', 1)
                utils.generateHelpContent(content, 'make-meeting-quick', 2)
                utils.generateHelpContent(content, 'make-poll', 3)
                utils.generateHelpContent(content, 'make-random', 4)
                utils.generateHelpContent(content, 'make-announcement', 5)
                utils.generateHelpContent(content, 'make-feedback', 6)

            elif input[2] in commands['meeting']:
                utils.generateHelpContent(content, 'make-meeting-complete', 1)
                utils.generateHelpContent(content, 'make-meeting-quick', 2)

            elif input[2] in commands['poll']:
                utils.generateHelpContent(content, 'make-poll', 1)

            elif input[2] in commands['random']:
                utils.generateHelpContent(content, 'make-random', 1)

            elif input[2] in commands['feedback']:
                utils.generateHelpContent(content, 'make-feedback', 1)
            
            else:
                message.channel.send(embed = utils.generateContent('Invalid command.'))
                return

        elif input[1]in commands['edit']:
            content = discord.Embed(
                title = 'Bot Documentation',
                colour = discord.Colour.green(),
                description = defaultDescription,
            )

            if len(input) == 2:
                utils.generateHelpContent(content, 'edit-meeting-complete', 1)
                utils.generateHelpContent(content, 'edit-meeting-quick-add', 2)
                utils.generateHelpContent(content, 'edit-meeting-quick-remove', 3)
                utils.generateHelpContent(content, 'edit-poll-add', 4)
                utils.generateHelpContent(content, 'edit-poll-remove', 5)

            elif input[2] in commands['meeting']:
                utils.generateHelpContent(content, 'edit-meeting-complete', 1)
                utils.generateHelpContent(content, 'edit-meeting-quick-add', 2)
                utils.generateHelpContent(content, 'edit-meeting-quick-remove', 3)

            elif input[2] in commands['poll']:
                if len(input) == 3:
                    utils.generateHelpContent(content, 'edit-poll-add', 1)
                    utils.generateHelpContent(content, 'edit-poll-remove', 2)

                elif input[3] in commands['add']:
                    utils.generateHelpContent(content, 'edit-poll-add', 1)

                elif input[3] in commands['remove']:
                    utils.generateHelpContent(content, 'edit-poll-remove', 1)

                else:
                    message.channel.send(embed = utils.generateContent('Invalid command.'))
                    return

            else:
                message.channel.send(embed = utils.generateContent('Invalid command.'))
                return

        elif input[1] in commands['delete']:
            content = discord.Embed(
                title = 'Bot Documentation',
                colour = discord.Colour.green(),
                description = 'Not available.'
            )

        elif input[1] in commands['meeting']:
            content = discord.Embed(
                title = 'Bot Documentation',
                colour = discord.Colour.green(),
                description = defaultDescription,
            )

            utils.generateHelpContent(content, 'make-meeting-complete', 1)
            utils.generateHelpContent(content, 'make-meeting-quick', 2)
            utils.generateHelpContent(content, 'edit-meeting-complete', 3)
            utils.generateHelpContent(content, 'edit-meeting-quick-add', 4)
            utils.generateHelpContent(content, 'edit-meeting-quick-remove', 5)

        elif input[1] in commands['poll']:
            content = discord.Embed(
                title = 'Bot Documentation',
                colour = discord.Colour.green(),
                description = defaultDescription,
            )

            utils.generateHelpContent(content, 'make-poll', 1)
            utils.generateHelpContent(content, 'edit-poll-add', 2)
            utils.generateHelpContent(content, 'edit-poll-remove', 3)

        elif input[1] in commands['random']:
            content = discord.Embed(
                title = 'Bot Documentation',
                colour = discord.Colour.green(),
                description = defaultDescription,
            )

            utils.generateHelpContent(content, 'make-random', 1)

        elif input[1] in commands['feedback']:
            content = discord.Embed(
                title = 'Bot Documentation',
                colour = discord.Colour.green(),
                description = defaultDescription,
            )

            utils.generateHelpContent(content, 'make-feedback', 1)

        elif input[1] in commands['announcement']:
            content = discord.Embed(
                title = 'Bot Documentation',
                colour = discord.Colour.green(),
                description = defaultDescription,
            )

            utils.generateHelpContent(content, 'make-announcement', 1)


        else:
            await message.channel.send(embed = utils.generateContent('Invalid command.'))
            return

        await message.channel.send(embed = content)
        await message.delete()

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
    await handlers.warnTextChannels(client)

scheduler.start()

client.run(discordToken)
