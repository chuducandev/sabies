import discord
from datetime import timedelta
from dateutil import parser
from dateutil import tz

def generateContent(content):
    return discord.Embed(
        description = content, 
        colour = discord.Colour.green()
    )

def generatePollContent(id, title, choices, selectedEmojis):
    description = '> ' + selectedEmojis[0] + ' ― ' + choices[0]

    for i in range(1, len(choices)):
        description += '\n> ' + selectedEmojis[i] + ' ― ' + choices[i]

    content = discord.Embed(
        title =  '**Poll #' + id + ': ' + title + '**',
        colour = discord.Colour.green(),
        description = description
    )

    content.set_footer(text = 'React this message to vote.')

    return content

def generateCompleteMeetingContent(id, title, dateTime, detail, accepted, declined):
    content = discord.Embed(
        title = '**Meeting #' + id + ': ' + title + '**',
        colour = discord.Colour.green(),
    )

    content.add_field(
        name = 'Date & Time',
        value = dateTime.astimezone(tz.gettz('Asia/Ho_Chi_Minh')).strftime('%b %d, %Y %I:%M %p') if dateTime != None else '-',
        inline = True,
    )

    content.add_field(
        name = 'Meeting Room',
        value = 'meeting-' + id,
        inline = True,
    )

    content.add_field(
        name = 'Google Calendar',
        value = '[Add this meeting to your calendar](http://www.google.com/calendar/event?action=TEMPLATE&text=' + '+'.join(title.split(' ')) + '&details=&location=&dates=' + dateTime.astimezone(tz.gettz('UTC')).strftime('%Y%m%dT%H%M%SZ') + '/' + (dateTime.astimezone(tz.gettz('UTC')) + timedelta(hours = 2)).strftime('%Y%m%dT%H%M%SZ') + ')',
        inline = False,
    )

    content.add_field(
        name = 'Meeting Detail',
        value = detail,
        inline = False
    )

    suffix = (' (' + str(len(accepted)) + ')') if len(accepted) > 0 else ''
    content.add_field(
        name = '😍 Accepted' + suffix,
        value = '> ' + '\n> '.join(map(lambda x: '<@!' + x + '>', accepted)) if accepted != None and len(accepted) > 0 else '-',
        inline = True
    )

    suffix = (' (' + str(len(declined)) + ')') if len(declined) > 0 else ''
    content.add_field(
        name = '🥲 Declined',
        value = '> ' + '\n> '.join(map(lambda x: '<@!' + x + '>', declined)) if declined != None and len(declined) > 0 else '-',
        inline = True
    )

    content.set_footer(text = 'React this message to respond.')

    return content

def generateDetail(blocks):
    detail = ''

    for block in blocks:
        if block[block['type']]['text'][0]['plain_text'] == '📘 Meeting Minutes':
            break
            
        if block['type'] == 'heading_1':
            continue

        if detail != '':
            detail += '\n'

        prefix = ''
        suffix = ''

        # if block['type'].startswith('heading'):
        #     prefix = '**'
        #     suffix = '**'

        if block['type'] == 'bulleted_list_item':
            prefix = '• ' 

        detail += prefix + block[block['type']]['text'][0]['plain_text'] + suffix

    return detail