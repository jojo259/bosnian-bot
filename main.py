print("init")

import os
import traceback

import discord

import commandslist
import config

class Bot(discord.Client):

	commandPrefix = '.'
	if config.debugMode:
		commandPrefix = ','

	async def on_ready(self):
		print(f'logged in as {self.user}')

	async def on_message(self, curMessage):

		if curMessage.author == self.user:
			return

		if curMessage.guild == None:
			mainServer = await self.fetch_guild(config.mainServerId)
			await curMessage.reply(f'bot only works in {mainServer.name}')
			return

		if curMessage.guild.id != config.mainServerId:
			return

		if len(curMessage.content) == 0:
			return

		if curMessage.content[0] != self.commandPrefix:
			return

		curMessageSplit = curMessage.content.split()

		for commandObj, commandAliases in commandslist.commandsList.items():
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
