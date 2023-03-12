import re
import random

import discord

import util

async def commandSetName(self, curMessage, curMessageSplit):
	
	targetId = util.parseTag(curMessageSplit[1])

	for curGuild in self.guilds:
		targetMember = await curGuild.fetch_member(targetId)
		if targetMember != None:
			break

	util.renameMember(targetMember, curMessageSplit[2])

	await curMessage.reply('renamed')

async def commandPartyMode(self, curMessage, curMessageSplit):

	def getEmojiName():
		newName = util.getRandomEmoji()
		while random.randint(1, 5) != 1:
			newName += util.getRandomEmoji()
		return newName

	if len(curMessageSplit) == 1:
		for curGuild in self.guilds:
			for curMember in curGuild.members:
				newName = getEmojiName()
				try:
					await util.renameMember(curMember, newName)
					print(f'renaming user {curMember.name} with id {curMember.id} to {newName}')
				except discord.errors.Forbidden as e:
					print(f'cannot rename user {curMember.name} with id {curMember.id}')
	elif len(curMessageSplit) == 2:
		targetId = util.parseTag(curMessageSplit[1])
		for curGuild in self.guilds:
			targetMember = await curGuild.fetch_member(targetId)
			if targetMember != None:
				break
		newName = getEmojiName()
		await util.renameMember(targetMember, newName)

	await curMessage.reply('party')

commandsList = {
	commandSetName: ['setname', 'name', 'rename', 'nick', 'renick', 'nickname', 'setnick'],
	commandPartyMode: ['partymode', 'party'],
}
