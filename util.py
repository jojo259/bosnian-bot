import random
import discord
import regex as re


def getRandomEmoji():
	with open('assets/emojis.txt', 'r', encoding = 'UTF-8') as emojisFile:
		emojisFileStrF = [re.findall(r'\X', line) for line in emojisFile]
		return random.choice(emojisFileStrF[0])


def parseTag(tagStr):
	targetId = re.search(r'<@[0-9]{1,}>', tagStr)
	targetId = re.search(r'[0-9]{1,}', targetId.group()).group()
	return targetId


async def renameMember(curMember, newName):
	try:
		await curMember.edit(nick = newName)
		print(f'renamed user {curMember.name} with id {curMember.id} to {newName}')
	except discord.errors.Forbidden as e:
		print(f'cannot rename user {curMember.name} with id {curMember.id}, forbidden')
