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
    
def generateRandomContent(id):
    return discord.Embed(
        title =  '**Please give a warm welcome to...**',
        colour = discord.Colour.green(),
        description = '<@!' + str(id) + '>'
    )

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

def generateQuickMeetingContent(id, createdAt, guestMembers, guestRoles):
    content = discord.Embed(
        title = '**Meeting #' + id + '**',
        colour = discord.Colour.green(),
    )

    content.add_field(
        name = 'Created at',
        value = createdAt.astimezone(tz.gettz('Asia/Ho_Chi_Minh')).strftime('%b %d, %Y %I:%M %p'),
        inline = False,
    )

    content.add_field(
        name = 'Meeting Room',
        value = 'meeting-' + id,
        inline = False,
    )

    guestContent = ''
    
    if guestMembers != None and guestRoles != None and len(guestMembers) + len(guestRoles) > 0:
        guestContent += '> ' + '\n> '.join(map(lambda x: '<@!' + x + '>', guestMembers)) + ('\n' if len(guestRoles) > 0 else '') if guestMembers != None and len(guestMembers) > 0 else ''
        guestContent += '> ' + '\n> '.join(map(lambda x: '<@&' + x + '>', guestRoles)) if guestRoles != None and len(guestRoles) > 0 else ''

    else:
        guestContent = '-'

    content.add_field(
        name = 'Guests',
        value = guestContent,
        inline = False,
    )

    # print(guestMembers)
    # print(guestRoles)

    return content

def generateDetail(blocks):
    detail = ''

    for block in blocks:
        if not('type' in block and block['type'] in block and 'text' in block[block['type']] and len(block[block['type']]['text']) > 0):
            continue
        
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

def generateHelpContent(content, command, i = 0):
    if command == '':
        content.add_field(
            name = '1. Commands',
            value = '**sabies** bot is designed for easy usage with three main commands `create` or `make`, `update` or `edit`, and `delete`.',
            inline = False
        )
        content.add_field(
            name = 'Creation',
            value = '`help create` or `help make`',
            inline = True
        )
        content.add_field(
            name = 'Edit',
            value = '`help update` or `help edit`',
            inline = True
        )
        content.add_field(
            name = 'Deletion',
            value = '`help delete`',
            inline = True
        )
        content.add_field(
            name = '2. Objects',
            value = '**sabies** bot now support three main objects, namely `meeting`, `poll` and `random`.',
            inline = False
        )
        content.add_field(
            name = 'Meetings',
            value = '`help meeting`',
            inline = True
        )
        content.add_field(
            name = 'Polls',
            value = '`help poll`',
            inline = True
        )
        content.add_field(
            name = 'Random people',
            value = '`help random`',
            inline = True
        )
        content.add_field(
            name = 'Announcements',
            value = '`help announcement`',
            inline = True
        )
        content.add_field(
            name = 'Feedback',
            value = '`help feedback`',
            inline = True
        )

    elif command == 'make-meeting-complete':
        content.add_field(
            name = str(i) + '. Create a complete meeting',
            value = '**Syntax:**\n`create meeting [<title>]`\n**Usage:**\nAfter this command is executed, a *Notion* page for this meeting will be created and its URL will be sent to the channels of the target departments. Click the link to finish the meeting detail.\n**Notes:**\n• Change value of the *Format* property to *Discord* when everything is filled. After that, the bot will send an announcement of the meeting to that channel.\n• All meetings created on *Notion* will be notified that way. This command is designed for the case that you are too lazy to open the *Meetings* page on *Notion*.\n• Only members responding *Accepted* to the announcement have the permission to view and connect the meeting channel.',
            inline = False
        )

    elif command == 'make-meeting-quick':
        content.add_field(
            name = str(i) + '. Create a quick meeting',
            value = '**Syntax:**\n`create meeting <tag_roles_or_people>`\n**Usage:**\nThis command can be used to create a private meeting channel without any specific information. Only members and roles mentioned in the command have the permission to view and connect that voice channel.',
            inline = False
        )

    elif command == 'make-poll':
        content.add_field(
            name = str(i) + '. Make a poll',
            value = '**Syntax:**\n`create poll <question> [| <answer_1> | <answer_2 | ...]`\n**Usage:** Use this command to create a multi-selection poll with the power of emoji reaction.\n**Notes:**\n• All parts in the command are separated with the character `|`.\n• Answers do not need to be included in the command. If no answers are included, two selections `Yes` and `No` are automatically added into the poll.\n• Each member can select multiple answers.',
            inline = False
        )

    elif command == 'make-random':
        content.add_field(
            name = str(i) + '. Select a random person',
            value = '**Syntax:**\n`create random <tag_people_or_roles_or_channels>`\n**Usage:** This command can be used to select randomly a person from a specific list.\n**Notes:**\n• The list includes all people tagged in the command or people currently belonging to any tagged roles or channel.\n• On the grounds that tagging voice channel has not been supported by Discord yet, users just need to list the name of target meeting\'s voice channel without any prefix characters.',
            inline = False
        )

    elif command == 'make-announcement':
        content.add_field(
            name = str(i) + '. Create an announcement',
            value = '**Syntax:**\n`create announcement <announcement>`\n**Usage:** With this command, a short announcement can be created and pinned on the source channel.\n',
            inline = False
        )

    elif command == 'make-feedback':
        content.add_field(
            name = str(i) + '. Send a feedback',
            value = '**Syntax:**\n`create feedback <feedback>`\n**Usage:** Users can use this command to send their feedback on the bot to the developer team.\n',
            inline = False
        )

    elif command == 'edit-meeting-complete':
        content.add_field(
            name = str(i) + '. Update a complete meeting',
            value = '**Syntax:**\n`update meeting <meeting_id>`\n**Usage:** After this command is executed, the bot will retrieve the target meeting\'s detail on *Notion* and update the announcement.\n**Notes:**Target departments cannot be updated after initialization.',
            inline = False
        )

    elif command == 'edit-meeting-quick-add':
        content.add_field(
            name = str(i) + '. Add people to a quick meeting',
            value = '**Syntax:**\n`update meeting <meeting_id> add <tag_people_or_roles>`\n**Usage:** This command can be used to allow a set people or roles to join into a specific quick meeting.',
            inline = False
        )

    elif command == 'edit-meeting-quick-remove':
        content.add_field(
            name = str(i) + '. Remove people from a quick meeting',
            value = '**Syntax:**\n`update meeting <meeting_id> remove <tag_people_or_roles>`\n**Usage:** This command can be used to remove the *Connect* and *View* permissions of a set of people or roles from a specific quick meeting. \n**Notes:** People having already joined into a meeting cannot be kicked with this command.',
            inline = False
        )
    
    elif command == 'edit-poll-add':
        content.add_field(
            name = str(i) + '. Add a selection to a poll',
            value = '**Syntax:**\n`update poll <poll_id> add <answer>`\n**Usage:** Users can use this command to add a selection to a specific poll.',
            inline = False
        )

    elif command == 'edit-poll-remove':
        content.add_field(
            name = str(i) + '. Remove a selection from a poll',
            value = '**Syntax:**\n`update poll <poll_id> remove <emoji_of_answer>`\n**Usage:** Users can use this command to remove a selection from a specific poll.',
            inline = False
        )

    elif command == '':
        content.add_field(
            name = str(i) + '. ',
            value = '**Syntax:**\n``\n**Usage:**\n',
            inline = False
        )