import re
import random
import discord
import util
import datetime
import command

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
		for curGuild in bot.guilds:
			for curMember in curGuild.members:
				if str(curMember.status) != 'offline' and not curMember.bot:
					onlineUsers.add(curMember)

		for curGuild in bot.guilds:
			for curVoiceChannel in curGuild.voice_channels:
				for curMember in curVoiceChannel.members:
					onlineUsers.add(curMember)

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
	CommandResetNames(): ['resetnames', 'resetname', 'reset']
}
