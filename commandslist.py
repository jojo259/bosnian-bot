import re
import random
import discord
import util
import datetime
import command
import openairequester
import chatgptreplacer
import time

class CommandSetReplacePrompt(command.Command):


	async def execute(self, bot, curMessage, curMessageSplit):
		if len(curMessageSplit) == 1:
			chatgptreplacer.userReplacePrompts.pop(curMessage.author.id, None)
			await curMessage.reply('unset')
			return
		chatgptreplacer.userReplacePrompts[curMessage.author.id] = ' '.join(curMessageSplit[1:])
		await curMessage.reply('set')


class CommandTranslateEmojis(command.Command):


	async def execute(self, bot, curMessage, curMessageSplit):
		conversation = []
		conversation.append(openairequester.constructMessage('system', f'Your task is to translate the user\'s message into emojis. You should reply with an appropriate number of emojis. If their message is simple then it will only require 1 emoji. Respond with ONLY emojis. The user said "{curMessage.content}".'))
		apiResp = openairequester.doRequest(conversation, curMessage.author.id)
		await curMessage.channel.send(apiResp[:2000])

class CommandAskChatGpt(command.Command):

	wpm = 250
	cpm = wpm * 5
	cps = cpm / 60

	async def execute(self, bot, curMessage, curMessageSplit):
		conversation = []
		conversation.append(openairequester.constructMessage('system', 'You are a helpful assistant.\nRespond very concisely.\nRespond with plain sentences only - do not add any extra formatting like lists or markdown and do not use any newlines.\nAlways use full-stops/periods (.) or question marks (?) or exclamation marks (!) at the end of sentences.\nUse a lot of funny emojis and try to be quirky.\nDo not put any emojis at the end of sentences - use emojis ONLY between words.'))
		conversation.append(openairequester.constructMessage('user', ' '.join(curMessageSplit[1:])))

		apiStartTime = time.time()
		apiResp = openairequester.doRequest(conversation, curMessage.author.id)
		apiEndTime = time.time()
		apiRespDuration = apiEndTime - apiStartTime

		sentences = re.findall(r'[^.!?]+[.!?]+', apiResp)

		async with curMessage.channel.typing():
			time.sleep(max(0, random.uniform(-0.5, 0.5) + len(sentences[0]) / CommandAskChatGpt.cps - apiRespDuration))
			await curMessage.reply(sentences[0])

		for sentence in sentences[1:]:
			async with curMessage.channel.typing():
				time.sleep(max(0, random.uniform(-0.5, 0.5) + len(sentence) / CommandAskChatGpt.cps))
				await curMessage.channel.send(sentence)

class CommandSetName(command.Command):


	async def execute(self, bot, curMessage, curMessageSplit):
		targetId = util.parseTag(curMessageSplit[1])

		for curGuild in bot.guilds:
			targetMember = await curGuild.fetch_member(targetId)
			if targetMember != None:
				break

		await util.renameMember(targetMember, curMessageSplit[2])
		await curMessage.reply('renamed')

class CommandPartyMode(command.Command):


	async def execute(self, bot, curMessage, curMessageSplit):

		def getEmojiName():
			newName = ''
			for i in range(random.randint(1, 3)):
				newName += util.getRandomEmoji()
			return newName

		if len(curMessageSplit) == 1:
			for curGuild in bot.guilds:
				for curMember in curGuild.members:
					newName = getEmojiName()
					await util.renameMember(curMember, newName)
		elif len(curMessageSplit) == 2:
			targetId = util.parseTag(curMessageSplit[1])
			for curGuild in bot.guilds:
				targetMember = await curGuild.fetch_member(targetId)
				if targetMember != None:
					break
			newName = getEmojiName()
			await util.renameMember(targetMember, newName)

		await curMessage.reply('party')

class CommandMuteRoulette(command.Command):


	async def execute(self, bot, curMessage, curMessageSplit):
		onlineUsers = set()
		if len(curMessageSplit) >= 2:
			onlineUsers.add(curMessage.author)
			for i, j in enumerate(curMessageSplit):
				if i == 0:
					continue
				try:
					targetId = util.parseTag(str(j))
				except:
					await curMessage.reply(f'target not found :(')
					return
				for curGuild in bot.guilds:
					targetMember = await curGuild.fetch_member(targetId)
					if not targetMember.bot:
						onlineUsers.add(targetMember)
					else:
						await curMessage.reply(f'bot found and ignored :(')

		else:
			for curGuild in bot.guilds:
				for curMember in curGuild.members:
					if str(curMember.status) != 'offline' and not curMember.bot:
						onlineUsers.add(curMember)

			for curGuild in bot.guilds:
				for curVoiceChannel in curGuild.voice_channels:
					for curMember in curVoiceChannel.members:
						if not curMember.bot:
							onlineUsers.add(curMember)

		if random.randint(1,2) == 1:
			unluckyUser = curMessage.author
		else:
			unluckyUser = random.choice(list(onlineUsers))

		timeoutSeconds = random.randint(1, 60)

		if random.randint(1, 5) == 1:
			timeoutSeconds *= random.randint(1, 5)
		try:
			await unluckyUser.timeout(datetime.timedelta(seconds = timeoutSeconds))
		except discord.errors.Forbidden as e:
			await curMessage.reply(f'tried to mute {unluckyUser.name} for {timeoutSeconds} seconds but forbidden :(')
			return
		await curMessage.reply(f'muted {unluckyUser.name} for {timeoutSeconds} seconds')

class CommandResetNames(command.Command):


	async def execute(self, bot, curMessage, curMessageSplit):
		for curGuild in bot.guilds:
			for curMember in curGuild.members:
				await util.renameMember(curMember, None)

		await curMessage.reply('reset')

commandsList = {
	CommandSetName(): ['setname', 'name', 'rename', 'nick', 'renick', 'nickname', 'setnick'],
	CommandPartyMode(): ['partymode', 'party'],
	CommandMuteRoulette(): ['roulette', 'muteroulette'],
	CommandResetNames(): ['resetnames', 'resetname', 'reset'],
	CommandAskChatGpt(): ['ask', 'chatgpt', 'query', 'question', 'q'],
	CommandSetReplacePrompt(): ['setreplaceprompt', 'replaceprompt', 'setreplace', 'replace', 'rewrite'],
	CommandTranslateEmojis(): [],
}
