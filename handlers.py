import requests
import json
import emojis
import utils
import os
import time
from notion_client import Client
from random import seed
from random import randint
from random import shuffle
from replit import db

# seed(10)

notionToken = os.environ('NOTION_TOKEN')

notion = Client(auth = notionToken)

hello = ['Hi there!', 'Hello!', 'Have a good day!', 'Tada!']

emojiList = list(emojis.db.get_emoji_aliases().values())

async def sayHello(message):
    await message.channel.send(hello[randint(0, 3)])

async def getQuote(message):
    response = requests.get('https://zenquotes.io/api/random')
    json_data = json.loads(response.text)
    quote = "*\"" + json_data[0]['q'] + "\"* ― " + json_data[0]['a']
    await message.channel.send(quote)

async def makePoll(message):
    #get new ID
    newID = str(int(db['polls']['maxId']) + 1)

    #get input
    input = message.content.split()

    #get title
    title = ''
    st = 2
    while st < len(input) and input[st] != '|':
        if input[st] != '':
            title += input[st] + ' '
        st += 1

    if title == '':
        await message.channel.send('Empty title is not accepted.')
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
        await message.channel.send('No selections are detected.')
        return

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
    await message.channel.send(newContent)
    lastMessage = message.channel.last_message

    for i in range(0, len(choices)):
        await lastMessage.add_reaction(selectedEmojis[i])

    #send speech
    await message.channel.send(
        'A new poll has just been created. Please make your own selection.', 
        tts = True, 
        delete_after = 7
    )

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
    time.sleep(7)
    await lastMessage.pin()
    await message.delete()

async def makeMeeting(message):
    #create a new meeting on Notion database
    newMeeting = notion.pages.create(**{
        'parent': {
            'database_id': '48f8fee9cd794180bc2fec0398253067',
        },
   	    'icon': {
    	    'type': "emoji",
			'emoji': emojiList
  	    },
        'properties': {
            'Name': {
                'title': [{
                    'text': {
                        'content': 'Tuscan Kale',
                    },
                }],
            },
            'Description': {
                'text': [
                {
                    text: {
                    content: 'A dark green leafy vegetable',
                    },
                },
                ],
            },
            'Food group': {
                select: {
                name: '🥦 Vegetable',
                },
            },
            Price: {
                number: 2.5,
            },
        },
    })

async def editPoll(message):
    #get input
    input = message.content.split()

    if len(input) <= 3:
        await message.channel.send('Invalid command.')
        return

    #get poll id
    id = input[2]

    #check if poll exists
    if not id in db['polls']:
        await message.channel.send('The poll #' + id + ' does not exist. Please try again.')
        return

    if db['polls'][id]['channel'] != str(message.channel):
        await message.channel.send('This poll does not belong to this channel.')
        return

    if input[3] == 'add':
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
        await pollMessage.edit(content = newContent)
        await pollMessage.add_reaction(newEmoji)

        await message.delete()
        await message.channel.send('Poll #' + id + ' has been updated.', tts = True)

    elif input[3] == 'remove':
        #check authority
        if str(message.author) != db['polls'][id]['author']:
            await message.channel.send('You do not have the authority to run this command.')
            return

        #check if choice exists
        if not input[4] in db['polls'][id]['selectedEmojis']:
            await message.channel.send('This choice could not be found. Please try again.')
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
        await pollMessage.edit(content = newContent)
        await pollMessage.clear_reaction(input[4])

        await message.delete()
        await message.channel.send('Poll #' + id + ' has been updated.', tts = True)

    else:
        await message.channel.send('Invalid command.')
        return

    