import random

def parseTag(tagStr):
	targetId = re.search(r'<@[0-9]{1,}>', curMessageSplit[1])
	targetId = re.search(r'[0-9]{1,}', targetId.group()).group()
	return targetId

async def renameMember(curMember, newName):
	try:
		await curMember.edit(nick = newName)
		print(f'renamed user {curMember.name} with id {curMember.id} to {newName}')
	except discord.errors.Forbidden as e:
		print(f'cannot rename user {curMember.name} with id {curMember.id}, forbidden')
