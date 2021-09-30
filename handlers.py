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
from keywords import commands

# seed(10)

notionToken = os.environ['NOTION_TOKEN']

notion = Client(auth = notionToken)

hello = [
    'Xin chào nhaaaa!! 😘', 
    'Chào nhé! 😎', 
    'Chúc bạn ngày mới tốt lành! 😊', 
    'Hú hà! 🤪'
]

textChannelWarnings = [
    'Ai ún cô cô nớt hôn? 🙄',
    'Sao hông ai nói gì hết vậy? Buồn á 😞',
    'Ai xuống nghe nhạc chung hông? 🎶',
    'Mấy bạn ở đây kiệm lời quá nè 🥲',
    'Quẩy lên đi mọi người ơi 🤪',
    'Ai iu em hong... 😧',
    'Mọi người hết iu em rồi... Nói gì đi chứ!! 😣',
    'Aloooo Alooooo 😮‍💨',
    'Chán quá ai nói chuyện cùng bé điiii 🙁',
    'Mỗi tin nhắn của mọi người sẽ sạc 0.0932019% năng lượng cho em đó... 😗',
    'Thèm quá... Thèm được nghe tiếng ai đó quá... 😟',
    'Hic, em tụt năng lượng rồi, giúp em với... 😖',
    'Mọi người ăn cơm chưa? 😀',
    'Heyo wassupp!!! Mọi người có gì mới không? 😆',
    'Đi mà, đi mà, nói gì gì đi mà... 🥺',
    'Cứ mỗi 24h mà không được nghe tiếng mọi người là em sẽ hết pin đó... 😔',
]

warnableTextChannels = [
    '872496182285434897', #general - sab
    '880487888628895784', #core - sab
    '880481462862876703', #fer
    '880481187615879208', #ea
    '880481532781932545', #hr
    '880481607662845953', #multi
    '880481561219321876', #volunteers
    '880481128069333122', #academy
    '880481583134543872', #sports
    # '880490415965499434', #advisors
    '883652475033362493', #guests 

]

emojiList = list(emojis.db.get_emoji_aliases().values())

departments = {
    'SAB & Friends': '872496182285434897',
    'SAB Cores': '880487888628895784',
    'SAB Finance & External Relations': '880481462862876703',
    'SAB Entertainment & Arts': '880481187615879208',
    'SAB Human Resources': '880481532781932545',
    'SAB Multimedia': '880481607662845953',
    'SAB Volunteers': '880481561219321876',
    'SAB Academy': '880481128069333122',
    'SAB Sports': '880481583134543872',
    'Test': '881169765220098049',
    'Test2': '881038773713002536',
}

async def sayHello(message):
    await message.channel.send(
        embed = utils.generateContent(hello[randint(0, len(hello)-1)])
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
            selected = randint(0, len(emojiList) - 1)
            while emojiList[selected] in selectedEmojis:
                selected = randint(0, len(emojiList) - 1)
            
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
                'emoji': emojiList[randint(0, len(emojiList) - 1)]
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
        #make a quick meeting

        #get new ID
        newID = str(int(db['meetings']['maxId']) + 1)

        #create new voice channel on Discord
        category = discord.utils.get(message.guild.categories, name = "Meetings")

        newVoiceChannel = await message.guild.create_voice_channel('meeting-' + newID, category = category)

        #get createdAt
        createdAt = datetime.now()

        #restrict @everyone permission
        await newVoiceChannel.set_permissions(message.guild.default_role, overwrite = discord.PermissionOverwrite(view_channel=False, connect = False, manage_channels = False))

        #init guests
        guestMembers = []
        guestRoles = []

        #set author permission
        await newVoiceChannel.set_permissions(message.author, overwrite = discord.PermissionOverwrite(view_channel=True, connect = True, manage_channels = False))

        for user in message.mentions:
            await newVoiceChannel.set_permissions(user, overwrite = discord.PermissionOverwrite(view_channel=True, connect = True, manage_channels = False))
            guestMembers.append(str(user.id))

        for role in message.role_mentions:
            await newVoiceChannel.set_permissions(role, overwrite = discord.PermissionOverwrite(view_channel=True, connect = True, manage_channels = False))
            guestRoles.append(str(role.id))

        #send announcement
        newMessage = await message.channel.send(embed = utils.generateQuickMeetingContent(newID, createdAt, guestMembers, guestRoles))

        #write meeting to database
        db['meetings'][newID] = {
            'type': 'quick',
            'author': str(message.author),
            'messages': newMessage.id,
            'textChannels': str(message.channel.id),
            'status': 'opened',
            'title': None,
            'time': None,
            'detail': None,
            'lastActive': None,
            'createdAt': str(createdAt),
            'channel': newVoiceChannel.id,
            'notion': None,
            'accepted': None,
            'declined': None,
            'guestMembers': guestMembers,
            'guestRoles': guestRoles,
        }

        db['voiceChannels'][newVoiceChannel.id] = {
            'meeting': newID,
        }

        db['meetings']['maxId'] = newID

        await message.delete()

async def makeRandom(message, input):
    #init random list
    randomList = []

    #add tagged users
    randomList.extend(list(map(lambda user: user.id, message.mentions)))

    #add members in tagged roles
    for role in message.role_mentions:
        randomList.extend(list(map(lambda user: user.id, role.members)))

    #add members in tagged text channels
    for channel in message.channel_mentions:
        randomList.extend(list(map(lambda user: user.id, channel.members)))

    #add members in tagged voice channels
    for channelName in input[2:]:
        channel = discord.utils.get(message.guild.voice_channels, name = channelName)
        
        if channel == None:
            continue

        randomList.extend(list(channel.voice_states.keys()))

    #remove duplicates in random list
    randomList = list(dict.fromkeys(randomList))
    # print(randomList)

    if len(randomList) <= 0:
        await message.channel.send(
            embed = utils.generateContent('The list is empty. Please try again.')
        )
        return

    #select randomly
    selection = randomList[randint(0, len(randomList) - 1)]

    #send announcement
    await message.channel.send(embed = utils.generateRandomContent(selection))


async def makeAnnouncement(message, input):
    #check authority
    authority = False
    acceptedRoles = ['SAB - Head of Department', 'SAB - Vice Head of Department', 'SAB - President', 'SAB - Vice President', 'SAB - Core']

    for role in message.author.roles:
        if str(role) in acceptedRoles:
            authority = True

    if not authority:
        await message.channel.send(
            embed = utils.generateContent('You do not have the permission to run this command.')
        )
        return

    #check if content is empty
    if len(input) <= 2:
        await message.channel.send(
            embed = utils.generateContent('You do not have the permission to run this command.')
        )
        return

    newMessage = await message.channel.send(embed = utils.generateContent(' '.join(input[2:])))
    await newMessage.pin()
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

    if input[3] in commands['add']:
        #generate new choice
        newChoice = ' '.join(input[4:])

        #random new emoji
        newEmoji = randint(0, len(emojiList) - 1)
        while emojiList[newEmoji] in db['polls'][id]['selectedEmojis']:
            newEmoji = randint(0, len(emojiList) - 1)

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

    elif input[3] in commands['remove']:
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

async def editMeeting(message, input):
    #get meeting id
    id = input[2]

    #check if meeting exists
    if not id in db['meetings']:
        await message.channel.send(
            embed = utils.generateContent('The meeting #' + id + ' does not exist. Please try again.')
        )
        return

    #check meeting status
    if db['meetings'][id]['status'] != 'opened':
        await message.channel.send(
            embed = utils.generateContent('This meeting had already been closed before.')
        )
        return

    #check meeting type
    if db['meetings'][id]['type'] != 'quick':
        await message.channel.send(
            embed = utils.generateContent('This type of meeting cannot be modified.')
        )
        return

    #check authority
    authority = (str(message.author) == str(db['meetings'][id]['author']))

    acceptedRoles = ['SAB - President', 'SAB - Vice President']

    for role in message.author.roles:
        if str(role) in acceptedRoles:
            authority = True

    if not authority:
        await message.channel.send(
            embed = utils.generateContent('You do not have the permission to run this command.')
        )
        return
        
    #fetch channel
    voiceChannel = message.guild.get_channel(db['meetings'][id]['channel'])
    
    if input[3] in commands['add']:
        for user in message.mentions:
            await voiceChannel.set_permissions(user, overwrite = discord.PermissionOverwrite(view_channel=True, connect = True, manage_channels = False))
            if not str(user.id) in db['meetings'][id]['guestMembers']:
                db['meetings'][id]['guestMembers'].append(str(user.id))

        for role in message.role_mentions:
            await voiceChannel.set_permissions(role, overwrite = discord.PermissionOverwrite(view_channel=True, connect = True, manage_channels = False))
            if not str(role.id) in db['meetings'][id]['guestRoles']:
                db['meetings'][id]['guestRoles'].append(str(role.id))

    elif input[3] in commands['remove']:
        for user in message.mentions:
            if str(user.id) == str(message.author.id):
                continue

            await voiceChannel.set_permissions(user, overwrite = discord.PermissionOverwrite(view_channel=False, connect = False, manage_channels = False))
            if str(user.id) in db['meetings'][id]['guestMembers']:
                db['meetings'][id]['guestMembers'].remove(str(user.id))

        for role in message.role_mentions:
            await voiceChannel.set_permissions(role, overwrite = discord.PermissionOverwrite(view_channel=False, connect = False, manage_channels = False))
            if str(role.id) in db['meetings'][id]['guestRoles']:
                db['meetings'][id]['guestRoles'].remove(str(role.id))

    else:
        await message.channel.send(
            embed = utils.generateContent('Invalid command.')
        )
        return

    #edit announcement
    channel = discord.utils.get(message.guild.channels, id = int(db['meetings'][id]['textChannels']))
    oldMessage = await channel.fetch_message(db['meetings'][id]['messages'])
    await oldMessage.edit(embed = utils.generateQuickMeetingContent(id, parser.parse(db['meetings'][id]['createdAt']), db['meetings'][id]['guestMembers'], db['meetings'][id]['guestRoles']))

    #send new announcement
    await message.channel.send(embed = utils.generateContent('Meeting #' + id + ' has been updated.'))
    await message.delete()

async def deleteMeeting(message, input):
    #get meeting id
    id = input[2]

    #check if meeting exists
    if not id in db['meetings']:
        await message.channel.send(
            embed = utils.generateContent('The meeting #' + id + ' does not exist. Please try again.')
        )
        return

    #check meeting status
    if db['meetings'][id]['status'] != 'opened':
        await message.channel.send(
            embed = utils.generateContent('This meeting had already been closed before.')
        )
        return

    #check authority
    if db['meetings'][id]['type'] == 'quick':
        if str(message.author) != str(db['meetings'][id]['author']):
            await message.channel.send(
                embed = utils.generateContent('You do not have the permission to run this command.')
            )
            return
    else:
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
        
    #fetch channel
    voiceChannel = message.guild.get_channel(db['meetings'][id]['channel'])
    
    #return if channel currently has member inside
    if voiceChannel.voice_states:
        await message.channel.send(
            embed = utils.generateContent('Cannot delete meetings with member inside.')
        )
        return
    
    #delete channel
    await voiceChannel.delete()

    #write to database
    db['meetings'][id]['status'] = 'closed'

    #send announcement
    await message.channel.send(embed = utils.generateContent('Meeting #' + id + ' has been deleted successfully.'))
    await message.delete()

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
        departmentChannelIds = db['meetings'][id]['textChannels']

        #get all channels of those departments
        def fetchDepartmentChannel(id):
            return discord.utils.get(payload.member.guild.channels, id = int(id))

        departmentChannels = list(map(lambda departmentChannelId: fetchDepartmentChannel(departmentChannelId), departmentChannelIds))

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

async def updateLastMessage(message):
    #check warnable text channel 
    if not str(message.channel.id) in warnableTextChannels:
        return

    db['lastChannelMessage'][str(message.channel.id)] = {
        'id': str(message.id),
        'author': str(message.author.id),
        'createdAt': str(message.created_at),
    }

async def cleanMeetings(client):
    for meeting in db['meetings']:
        if 'status' in db['meetings'][meeting] and db['meetings'][meeting]['status'] == 'opened':
            if not 'createdAt' in db['meetings'][meeting]:
                continue

            if not 'lastActive' in db['meetings'][meeting]:
                continue

            if not 'channel' in db['meetings'][meeting]:
                continue

            if 'time' in db['meetings'][meeting]:
                dateTime = db['meetings'][meeting]['time']
                if dateTime != None:
                    dateTime = parser.parse(dateTime)
                    if dateTime.astimezone(tz.gettz('UTC')) > datetime.now().astimezone(tz.gettz('UTC')):
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

    def fetchDepartmentChannel(id):
            return discord.utils.get(client.guilds[0].channels, id = int(id))

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
        departmentChannelIds = list(map(lambda departmentTag: departments[departmentTag['name']], departmentTags))
        print(departmentChannelIds)

        #get all channels of those departments
        departmentChannels = list(map(lambda departmentChannelId: fetchDepartmentChannel(departmentChannelId), departmentChannelIds))

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
            await message.pin()

            messages.append(message.id)

        #create new voice channel on Discord
        category = discord.utils.get(client.guilds[0].categories, name = "Meetings")

        newVoiceChannel = await client.guilds[0].create_voice_channel('meeting-' + newID, category = category)

        #restrict @everyone permission
        await newVoiceChannel.set_permissions(client.guilds[0].default_role, overwrite = discord.PermissionOverwrite(view_channel=False, connect = False, manage_channels = False))

        #write meeting to database
        db['meetings'][newID] = {
            'type': 'complete',
            'author': None,
            'messages': messages,
            'textChannels': departmentChannelIds,
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
            'guestMembers': None,
            'guestRoles': None,
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

async def warnTextChannels(client):
    if datetime.now().hour >= 22-7 or datetime.now().hour < 7-7:
        return

    for id in warnableTextChannels:
        if id in db['lastChannelMessage']:
            if str(db['lastChannelMessage'][id]['author']) == str(client.user.id):
                if datetime.now().astimezone(tz.gettz('UTC')) - parser.parse(db['lastChannelMessage'][id]['createdAt']).astimezone(tz.gettz('UTC')) <= timedelta(hours = 1):
                    continue
            else:
                if datetime.now().astimezone(tz.gettz('UTC')) - parser.parse(db['lastChannelMessage'][id]['createdAt']).astimezone(tz.gettz('UTC')) <= timedelta(days = 1):
                    continue
        
        #send message
        channel = discord.utils.get(client.guilds[0].text_channels, id = int(id))
        message = await channel.send(embed = utils.generateContent(textChannelWarnings[randint(0, len(textChannelWarnings) - 1)]))

        #write to database
        db['lastChannelMessage'][id] = {
            'id': str(message.id),
            'author': str(message.author.id),
            'createdAt': str(message.created_at),
        }
