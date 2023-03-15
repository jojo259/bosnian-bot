import re
import random
import discord
import util
import datetime

async def commandSetName(self, curMessage, curMessageSplit):

	targetId = util.parseTag(curMessageSplit[1])

	for curGuild in self.guilds:
		targetMember = await curGuild.fetch_member(targetId)
		if targetMember != None:
			break

	await util.renameMember(targetMember, curMessageSplit[2])

	await curMessage.reply('renamed')

async def commandPartyMode(self, curMessage, curMessageSplit):

	def getEmojiName():
		newName = ''
		for i in range(random.randint(1, 3)):
			newName += util.getRandomEmoji()
		return newName

	if len(curMessageSplit) == 1:
		for curGuild in self.guilds:
			for curMember in curGuild.members:
				newName = getEmojiName()
				await util.renameMember(curMember, newName)
	elif len(curMessageSplit) == 2:
		targetId = util.parseTag(curMessageSplit[1])
		for curGuild in self.guilds:
			targetMember = await curGuild.fetch_member(targetId)
			if targetMember != None:
				break
		newName = getEmojiName()
		await util.renameMember(targetMember, newName)

	await curMessage.reply('party')

async def commandMuteRoulette(self, curMessage, curMessageSplit=None):
	onlineUsers = []
	for curGuild in self.guilds:
		for curMember in curGuild.members:
			if str(curMember.status) != 'offline' and not curMember.bot:
				onlineUsers.append(curMember)

	unluckyUser = random.choice(onlineUsers)
	timeoutSeconds = random.randint(1, 60)
	if random.randint(1, 5) == 1:
		timeoutSeconds *= random.randint(1, 5)
	try:
		await unluckyUser.timeout(datetime.timedelta(seconds = timeoutSeconds))
	except discord.errors.Forbidden as e:
		await curMessage.reply(f'tried to mute {unluckyUser.name} for {timeoutSeconds} seconds but forbidden :(')
		return
	await curMessage.reply(f'muted {unluckyUser.name} for {timeoutSeconds} seconds')

async def commandResetNames(self, curMessage, curMessageSplit):
	for curGuild in self.guilds:
		for curMember in curGuild.members:
			await util.renameMember(curMember, None)

	await curMessage.reply('reset')

commandsList = {
	commandSetName: ['setname', 'name', 'rename', 'nick', 'renick', 'nickname', 'setnick'],
	commandPartyMode: ['partymode', 'party'],
	commandMuteRoulette: ['roulette', 'muteroulette'],
	commandResetNames: ['resetnames', 'resetname', 'reset']
}

