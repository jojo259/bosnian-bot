import openairequester
import json
import regex as re
import discord

userReplacePrompts = {}

async def checkReplace(bot, curMessage):

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

	print(f'replacing message by {curMessage.author.name}')

	conversation = []
	conversation.append(openairequester.constructMessage('system', requestPrompt))
	apiResp = openairequester.doRequest(conversation)

	try:
		apiResp = json.loads(apiResp)['rewrittenMessage']
	except json.JSONDecodeError as e:
		print(f'JSON Decode Error, attempting to fix JSON: {apiResp}')
		foundJson = re.search(r'\{(.|\n)*\}', apiResp)
		if foundJson:
			print(f'Fixed JSON')
			try:
				apiResp = json.loads(foundJson.group())['rewrittenMessage']
			except json.JSONDecodeError as e:
				print('Could not fix JSON')
				await curMessage.reply(apiResp)
				return

	authorWebhook = None
	channelWebhooks = await curMessage.channel.webhooks()
	for curWebhook in channelWebhooks:
		if curWebhook.name == 'bosnian-bot-user-mimic':
			authorWebhook = curWebhook
	
	pattern = r"<@(\d+)>"
	tags = re.findall(pattern, apiResp)
	if len(tags) > 0:
		for i in tags:
			print(i)
			for curGuild in bot.guilds:
				try:
					pattern = r"<@({})>"
					user = await curGuild.fetch_member(i)
					userPattern = pattern.format(i)
					apiResp = re.sub(userPattern, f"{user.name}", apiResp)
				except:
					pass


	if authorWebhook == None:
		authorWebhook = await curMessage.channel.create_webhook(name = 'bosnian-bot-user-mimic')
	await curMessage.delete()
	await authorWebhook.send(apiResp, username = curMessage.author.name, avatar_url = curMessage.author.display_avatar.url, allowed_mentions = discord.AllowedMentions(users = True, roles = False, everyone = False))
