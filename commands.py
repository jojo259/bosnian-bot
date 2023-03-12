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

commandsList = {
	commandSetName: ['setname', 'name', 'rename', 'nick', 'renick', 'nickname', 'setnick'],
}
