import re
import random

import discord

async def commandSetName(self, curMessage, curMessageSplit):
	
	targetId = re.search(r'<@[0-9]{1,}>', curMessageSplit[1])
	targetId = re.search(r'[0-9]{1,}', targetId.group()).group()

	for curGuild in self.guilds:
		targetUser = await curGuild.fetch_member(targetId)
		if targetUser != None:
			break

	print(f'renaming user {targetUser.name} with id {targetUser.id} to {curMessageSplit[2]}')

	await targetUser.edit(nick = curMessageSplit[2])
	await curMessage.reply('renamed')

commandsList = {
	commandSetName: ['setname', 'name', 'rename', 'nick', 'renick', 'nickname', 'setnick'],
}
