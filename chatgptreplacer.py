import openairequester

userReplacePrompts = {}

async def checkReplace(curMessage):

	if curMessage.author.id not in userReplacePrompts:
		return

	requestPrompt = f'Task: The user has requested that you rewrite this message using the prompt given below. Rewrite the message and respond with only the rewritten message. If you do not understand how to rewrite it or are unable to, then respond only with the word "error".\nUser prompt: {userReplacePrompts[curMessage.author.id]}\nUser name: {curMessage.author.name}\nUser message is as follows:\n{curMessage.content}'

	print(requestPrompt)

	replacedText = openairequester.doRequest(requestPrompt)

	authorWebhook = None
	channelWebhooks = await curMessage.channel.webhooks()
	for curWebhook in channelWebhooks:
		if curWebhook.name == 'bosnian-bot-user-mimic':
			authorWebhook = curWebhook

	if authorWebhook == None:
		authorWebhook = await curMessage.channel.create_webhook(name = 'bosnian-bot-user-mimic')
	await authorWebhook.send(replacedText, username = curMessage.author.name, avatar_url = curMessage.author.display_avatar.url)
	await curMessage.delete()
