print("init")

import os
import traceback

import discord

import commands
import config

class Bot(discord.Client):

	debugMode = False
	if 'debug' in os.environ:
		debugMode = True
	commandPrefix = '.'
	if debugMode:
		commandPrefix = ','

	async def on_ready(self):
		print(f'logged in as {self.user}')

	async def on_message(self, curMessage):
		curAuthor = curMessage.author
		if curAuthor == self.user:
			return

		if len(curMessage.content) == 0:
			return

		if curMessage.content[0] != self.commandPrefix:
			return

		curMessageSplit = curMessage.content.split()

		for commandObj, commandAliases in commands.commandsList.items():
			for curAlias in commandAliases:
				if curMessageSplit[0][1:] == curAlias:
					print(f'user {curMessage.author.name} with id {curMessage.author.id} sent command: {curMessage.content}')
					async with curMessage.channel.typing():
						try:
							await commandObj.execute(self, curMessage, curMessageSplit)
						except Exception as e:
							stackTraceStr = traceback.format_exc()
							print(stackTraceStr)
							await curMessage.reply(f'errored:\n{stackTraceStr}')

if __name__ == '__main__':

	intents = discord.Intents.default()
	intents.presences = True
	intents.message_content = True
	intents.members = True
	bot = Bot(intents = intents)
	bot.run(config.botToken)
