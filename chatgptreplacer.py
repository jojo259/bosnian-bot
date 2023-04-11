import openairequester
import json

userReplacePrompts = {}

async def checkReplace(curMessage):

	if curMessage.author.id not in userReplacePrompts:
		return

	requestPrompt = json.dumps(
		{
			'task': 'The user has requested that you rewrite this message using their instructions. Respond in JSON, with the format {"rewrittenMessage": "<message>"}. Do not respond with anything other than the JSON.',
			'userInstructions': userReplacePrompts[curMessage.author.id],
			'userName': curMessage.author.name,
			'userMessage': curMessage.content,
		}
	)

	print(requestPrompt)

	apiResp = openairequester.doRequest(requestPrompt)

	try:
		apiResp = json.loads(apiResp)['rewrittenMessage']
	except json.decoder.JSONDecodeError as e:
		print('decoding chatgpt replacer json failed')
		await curMessage.reply(apiResp)
		return

	authorWebhook = None
	channelWebhooks = await curMessage.channel.webhooks()
	for curWebhook in channelWebhooks:
		if curWebhook.name == 'bosnian-bot-user-mimic':
			authorWebhook = curWebhook

	if authorWebhook == None:
		authorWebhook = await curMessage.channel.create_webhook(name = 'bosnian-bot-user-mimic')
	await curMessage.delete()
	await authorWebhook.send(apiResp, username = curMessage.author.name, avatar_url = curMessage.author.display_avatar.url)
