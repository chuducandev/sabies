import discord
import requests
import json
import emojis
import utils
import os
import time
from datetime import datetime
from datetime import timedelta
from dateutil import parser
from dateutil import tz
from notion_client import Client
from random import seed
from random import randint
from random import shuffle
from replit import db

# seed(10)

notionToken = os.environ['NOTION_TOKEN']

notion = Client(auth = notionToken)

hello = ['Hi there!', 'Hello!', 'Have a good day!', 'Tada!']

emojiList = list(emojis.db.get_emoji_aliases().values())

departments = {
    'SAB & Friends': 'general',
    'SAB Cores': 'cores',
    'SAB Finance & External Relations': 'finance-external-relations',
    'SAB Entertainment & Arts': 'entertainment-arts',
    'SAB Human Resources': 'human-resources',
    'SAB Multimedia': 'multimedia',
    'SAB Volunteers': 'volunteers',
    'SAB Academy': 'academy',
    'SAB Sports': 'sports',
    'Test': 'test-bot',
    'Test2': 'test-bot-2',
}

async def sayHello(message):
    await message.channel.send(
        embed = utils.generateContent(hello[randint(0, 3)])
    )

async def getQuote(message):
    response = requests.get('https://zenquotes.io/api/random')
    json_data = json.loads(response.text)
    quote = "*\"" + json_data[0]['q'] + "\"* ― " + json_data[0]['a']
    await message.channel.send(
        embed = utils.generateContent(quote)
    )

async def makePoll(message, input):
    #get new ID
    newID = str(int(db['polls']['maxId']) + 1)

    #get title
    title = ''
    st = 2
    while st < len(input) and input[st] != '|':
        if input[st] != '':
            title += input[st] + ' '
        st += 1

    if title == '':
        await message.channel.send(
            embed = utils.generateContent('Empty title is not accepted.')
        )
        return

    #get choices
    choices = ['']
    for i in range(st+1, len(input)):
        if input[i] == '':
            continue

        if input[i] == '|' and choices[len(choices)-1] != '':
            choices.append('')
        else:
            choices[len(choices)-1] += input[i] + ' '
    
    if choices[len(choices)-1] == '':
        choices.pop()

    if len(choices) == 0:
        choices = ['Yes', 'No']
        selectedEmojis = ['😘', '😡']
    else:
        #random emojis
        selectedEmojis = []
        for i in range(0, len(choices)):
            selected = randint(0, len(emojiList))
            while emojiList[selected] in selectedEmojis:
                selected = randint(0, len(emojiList))
            
            selectedEmojis.append(emojiList[selected])

    #generate content
    newContent = utils.generatePollContent(newID, title, choices, selectedEmojis)

    #send message
    await message.channel.send(embed = newContent)
    lastMessage = message.channel.last_message

    for i in range(0, len(choices)):
        await lastMessage.add_reaction(selectedEmojis[i])

    #add poll to database
    db['polls'][newID] = {
        'message': str(lastMessage.id),
        'author': str(message.author),
        'channel': str(message.channel),
        'title': title,
        'choices': choices,
        'selectedEmojis': selectedEmojis,
    }
    db['polls']['maxId'] = newID

    #delete command and pin message
    await lastMessage.pin()
    await message.delete()

async def makeMeeting(message, input):
    if len(message.mentions) == 0 and len(message.role_mentions) == 0:
        #make a complete meeting

        #check authority
        authority = False
        acceptedRoles = ['Head of Department', 'Vice Head of Department', 'President', 'Vice President', 'Core']

        for role in message.author.roles:
            if str(role) in acceptedRoles:
                authority = True

        if not authority:
            await message.channel.send(
                embed = utils.generateContent('You do not have the permission to run this command.')
            )
            return

        #get title
        if len(input) > 2:
            title = ' '.join(input[2:])
        else:
            title = 'Untitled'

        #create a new meeting on Notion database
        newMeeting = notion.pages.create(**{
            'parent': {
                'database_id': 'd3514f3a073a424f8fddb333db529d93',
            },
            'icon': {
                'type': "emoji",
                'emoji': emojiList[randint(0, len(emojiList))]
            },
            'properties': {
                "Name": {
                    "title": [{
                        "text": {
                            "content": title
                        }
                    }]
                },
            },
        })

        await message.channel.send(
            embed = utils.generateContent('A new meeting has been created. Please complete all information on this Notion page.\nhttps://www.notion.so/sabvn/' + ''.join(newMeeting['id'].split('-')) + '\n**Notes:** Change the *Format* property to *Discord* **when you\'re done**.')
        )

        await message.delete()
    
    else: 
        #make a quick makeMeeting

        #get new ID
        newID = str(int(db['meetings']['maxId']) + 1)

        #create new voice channel on Discord
        category = discord.utils.get(message.guild.categories, name = "Meeting Rooms")

        newVoiceChannel = await message.guild.create_voice_channel('meeting-' + newID, category = category)

        #restrict @everyone permission
        await newVoiceChannel.set_permissions(message.guild.default_role, overwrite = discord.PermissionOverwrite(view_channel=False, connect = False, manage_channels = False))

        #set author permission
        await newVoiceChannel.set_permissions(message.author, overwrite = discord.PermissionOverwrite(view_channel=True, connect = True, manage_channels = False))

        for user in message.mentions:
            await newVoiceChannel.set_permissions(user, overwrite = discord.PermissionOverwrite(view_channel=True, connect = True, manage_channels = False))

        for role in message.role_mentions:
            await newVoiceChannel.set_permissions(role, overwrite = discord.PermissionOverwrite(view_channel=True, connect = True, manage_channels = False))

        #write meeting to database
        db['meetings'][newID] = {
            'type': 'quick',
            'messages': None,
            'textChannels': None,
            'status': 'opened',
            'title': None,
            'time': None,
            'detail': None,
            'lastActive': None,
            'createdAt': str(datetime.now()),
            'channel': newVoiceChannel.id,
            'notion': None,
            'accepted': None,
            'declined': None,
        }

        db['voiceChannels'][newVoiceChannel.id] = {
            'meeting': newID,
        }

        db['meetings']['maxId'] = newID

        #delete command
        await message.delete()


async def editPoll(message, input):
    if len(input) <= 3:
        await message.channel.send(
            embed = utils.generateContent('Invalid command.')
        )
        return

    #get poll id
    id = input[2]

    #check if poll exists
    if not id in db['polls']:
        await message.channel.send(
            embed = utils.generateContent('The poll #' + id + ' does not exist. Please try again.')
        )
        return

    if db['polls'][id]['channel'] != str(message.channel):
        await message.channel.send(
            embed = utils.generateContent('This poll does not belong to this channel.')
        )
        return

    if input[3] == 'add' or input[3] == 'a':
        #generate new choice
        newChoice = ' '.join(input[4:])

        #random new emoji
        newEmoji = randint(0, len(emojiList))
        while emojiList[newEmoji] in db['polls'][id]['selectedEmojis']:
            newEmoji = randint(0, len(emojiList))

        newEmoji = emojiList[newEmoji]

        #add new choice to database
        db['polls'][id]['choices'].append(newChoice)
        db['polls'][id]['selectedEmojis'].append(newEmoji)

        #generate new content
        newContent = utils.generatePollContent(
            id, 
            db['polls'][id]['title'], 
            db['polls'][id]['choices'], 
            db['polls'][id]['selectedEmojis']
        )

        #edit poll message
        pollMessage = await message.channel.fetch_message(db['polls'][id]['message'])
        await pollMessage.edit(embed = newContent)
        await pollMessage.add_reaction(newEmoji)

        await message.delete()
        await message.channel.send(
            embed = utils.generateContent('Poll #' + id + ' has been updated.')
        )

    elif input[3] == 'remove' or input[3] == 'r':
        #check authority
        if str(message.author) != db['polls'][id]['author']:
            await message.channel.send(
                embed = utils.generateContent('You do not have the authority to run this command.')
            )
            return

        #check if choice exists
        if not input[4] in db['polls'][id]['selectedEmojis']:
            await message.channel.send(
                embed = utils.generateContent('This choice could not be found. Please try again.')
            )
            return

        #remove choice in database
        index = db['polls'][id]['selectedEmojis'].index(input[4])
        db['polls'][id]['choices'].pop(index)
        db['polls'][id]['selectedEmojis'].pop(index)

        #generate new content
        newContent = utils.generatePollContent(
            id,
            db['polls'][id]['title'], 
            db['polls'][id]['choices'], 
            db['polls'][id]['selectedEmojis']
        )

        #edit poll message
        pollMessage = await message.channel.fetch_message(db['polls'][id]['message'])
        await pollMessage.edit(embed = newContent)
        await pollMessage.clear_reaction(input[4])

        await message.delete()
        await message.channel.send(
            embed = utils.generateContent('Poll #' + id + ' has been updated.')
        )

    else:
        await message.channel.send(
            embed = utils.generateContent('Invalid command.')
        )
        return

async def updateMeetingLastActive(before):
    if before.channel != None and str(before.channel.id) in db['voiceChannels']:
        meeting = db['voiceChannels'][str(before.channel.id)]['meeting']
        db['meetings'][meeting]['lastActive'] = str(datetime.now())

async def updateMeetingAttendances(payload):
    #check if message belongs to a meeting
    if not str(payload.message_id) in db['meetingMessages']:
        return

    #get id
    id = db['meetingMessages'][str(payload.message_id)]['meeting']

    #return if quick meeting
    if db['meetings'][id]['type'] != 'complete':
        return

    #get voice channel
    voiceChannel = discord.utils.get(payload.member.guild.channels, name = 'meeting-' + id)

    #edit permission
    if voiceChannel != None:
        if payload.emoji.name == '😍':
            if str(payload.member.id) in db['meetings'][id]['accepted']:
                #remove accept
                db['meetings'][id]['accepted'].remove(str(payload.member.id))
                
                await voiceChannel.set_permissions(payload.member, overwrite = discord.PermissionOverwrite(view_channel=False, connect = False, manage_channels = False))
            
            else:
                #add accept
                db['meetings'][id]['accepted'].append(str(payload.member.id))
                
                if str(payload.member.id) in db['meetings'][id]['declined']:
                    db['meetings'][id]['declined'].remove(str(payload.member.id))
                
                await voiceChannel.set_permissions(payload.member, overwrite = discord.PermissionOverwrite(view_channel=True, connect = True, manage_channels = False))
        
        elif payload.emoji.name == '🥲':
            if str(payload.member.id) in db['meetings'][id]['declined']:
                #remove decline
                db['meetings'][id]['declined'].remove(str(payload.member.id))
            
            else:
                #add decline
                db['meetings'][id]['declined'].append(str(payload.member.id))
                
                if str(payload.member.id) in db['meetings'][id]['accepted']:
                    db['meetings'][id]['accepted'].remove(str(payload.member.id))
                
                await voiceChannel.set_permissions(payload.member, overwrite = discord.PermissionOverwrite(view_channel=False, connect = False, manage_channels = False))

        #get department names
        departmentChannelNames = db['meetings'][id]['textChannels']

        #get all channels of those departments
        def fetchDepartmentChannel(name):
            return discord.utils.get(payload.member.guild.channels, name = name)

        departmentChannels = list(map(lambda departmentChannelName: fetchDepartmentChannel(departmentChannelName), departmentChannelNames))

        #get the message ids
        messages = db['meetings'][id]['messages']

        #get meeting info
        title = db['meetings'][id]['title']
        dateTime = parser.parse(db['meetings'][id]['time'])
        detail = db['meetings'][id]['detail']
        accepted = db['meetings'][id]['accepted']
        declined = db['meetings'][id]['declined']

        #edit messages
        for i in range(0, len(departmentChannels)):
            message = await departmentChannels[i].fetch_message(messages[i])
            
            await message.edit(embed = utils.generateCompleteMeetingContent(
                id = id,
                title = title,
                dateTime = dateTime,
                detail = detail,
                accepted = accepted,
                declined = declined,
            ))

    textChannel = discord.utils.get(payload.member.guild.channels, id = payload.channel_id)
    message = await textChannel.fetch_message(payload.message_id)

    await message.remove_reaction(payload.emoji, payload.member)


async def cleanMeetings(client):
    for meeting in db['meetings']:
        if 'status' in db['meetings'][meeting] and db['meetings'][meeting]['status'] == 'opened':
            if not 'createdAt' in db['meetings'][meeting]:
                continue

            if not 'lastActive' in db['meetings'][meeting]:
                continue

            if not 'channel' in db['meetings'][meeting]:
                continue

            lastActive = db['meetings'][meeting]['lastActive']
            createdAt = db['meetings'][meeting]['createdAt']

            createdAt = parser.parse(createdAt).astimezone(tz.gettz('UTC'))

            if lastActive == None:
                #delete after a day of inactivity
                if datetime.now().astimezone(tz.gettz('UTC')) - createdAt <= timedelta(hours = 24):
                    continue
            else:
                lastActive = parser.parse(lastActive).astimezone(tz.gettz('UTC'))
                
                #delete after an hour the meeting ends
                if datetime.now().astimezone(tz.gettz('UTC')) - lastActive <= timedelta(hours = 1):
                    continue

            #fetch channel
            voiceChannel = client.get_channel(db['meetings'][meeting]['channel'])
            
            #return if channel currently has member inside
            if voiceChannel.voice_states:
                continue
            
            #delete channel
            await voiceChannel.delete()

            #write to database
            db['meetings'][meeting]['status'] = 'closed'

async def checkNotionMeetings(client):
    results = notion.databases.query(
        database_id = 'd3514f3a073a424f8fddb333db529d93',
        filter = {
            "property": "Format", 
            "select": {
                "equals": 'Discord'
            }
        }
    ).get('results')

    def fetchDepartmentChannel(name):
            return discord.utils.get(client.guilds[0].channels, name = name)

    for result in results:
        #check if this notion has been checked
        if result['id'] in db['notionMeetings']:
            continue

        # print(result)
        # print(notion.blocks.children.list(block_id = result['id']).get('results'))
        # continue

        #get new ID
        newID = str(int(db['meetings']['maxId']) + 1)

        #get departments
        departmentTags = result['properties']['Department']['multi_select']
        departmentChannelNames = list(map(lambda departmentTag: departments[departmentTag['name']], departmentTags))

        #get all channels of those departments
        departmentChannels = list(map(lambda departmentChannelName: fetchDepartmentChannel(departmentChannelName), departmentChannelNames))

        #get the content of Notion meeting
        blocks = notion.blocks.children.list(block_id = result['id']).get('results')

        #initiate the message list
        messages = []

        #get title of meeting
        title = result['properties']['Name']['title'][0]['plain_text'] if len(result['properties']['Name']['title']) > 0 else ''

        #get date and time of meeting
        dateTime = parser.parse(result['properties']['Date']['date']['start']) if 'Date' in result['properties'] else None

        #get the meeting detail
        detail = utils.generateDetail(blocks)

        #send messages
        for departmentChannel in departmentChannels:
            message = await departmentChannel.send(embed = utils.generateCompleteMeetingContent(
                id = newID,
                title = title,
                dateTime = dateTime,
                detail = detail,
                accepted = [],
                declined = [],
            ))

            await message.add_reaction('😍')
            await message.add_reaction('🥲')

            messages.append(message.id)

        #create new voice channel on Discord
        category = discord.utils.get(client.guilds[0].categories, name = "Meeting Rooms")

        newVoiceChannel = await client.guilds[0].create_voice_channel('meeting-' + newID, category = category)

        #restrict @everyone permission
        await newVoiceChannel.set_permissions(client.guilds[0].default_role, overwrite = discord.PermissionOverwrite(view_channel=False, connect = False, manage_channels = False))

        #write meeting to database
        db['meetings'][newID] = {
            'type': 'complete',
            'messages': messages,
            'textChannels': departmentChannelNames,
            'status': 'opened',
            'title': title,
            'time': str(dateTime.astimezone(tz.gettz('UTC'))),
            'detail': detail,
            'lastActive': str(dateTime.astimezone(tz.gettz('UTC'))),
            'createdAt': str(datetime.now()),
            'channel': newVoiceChannel.id,
            'notion': result['id'],
            'accepted': [],
            'declined': [],
        }

        db['voiceChannels'][newVoiceChannel.id] = {
            'meeting': newID,
        }

        db['notionMeetings'][result['id']] = {
            'meeting': newID,
        }

        for message in messages:
            db['meetingMessages'][message] = {
                'meeting': newID,
            }

        db['meetings']['maxId'] = newID
