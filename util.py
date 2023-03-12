import random

def parseTag(tagStr):
	targetId = re.search(r'<@[0-9]{1,}>', curMessageSplit[1])
	targetId = re.search(r'[0-9]{1,}', targetId.group()).group()
	return targetId
