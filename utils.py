def generatePollContent(id, title, choices, selectedEmojis):
    content = '**Poll #' + id + ': ' + title + '**'

    for i in range(0, len(choices)):
        content += '\n' + selectedEmojis[i] + ' ― ' + choices[i]

    content += '\n*React this message to vote.*'

    return content