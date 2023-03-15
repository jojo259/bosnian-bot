print("init")

import os
import traceback

import discord
import dotenv

import commands

dotenv.load_dotenv()

botToken = os.environ['bottoken']

class Bot(discord.Client):

	commandPrefix = '.'

	async def on_message(self, curMessage):
		curAuthor = curMessage.author
		if curAuthor == self.user:
			return

		if len(curMessage.content) == 0:
			return

		if curMessage.content[0] != self.commandPrefix:
			return

		curMessageSplit = curMessage.content.split()

		for commandFunc, commandAliases in commands.commandsList.items():
			for curAlias in commandAliases:
				if curMessageSplit[0][1:] == curAlias:
					print(f'user {curMessage.author.name} with id {curMessage.author.id} sent command: {curMessage.content}')
					async with curMessage.channel.typing():
						try:
							await commandFunc(self, curMessage, curMessageSplit)
						except Exception as e:
							stackTraceStr = traceback.format_exc()
							print(stackTraceStr)
							await curMessage.reply(f'errored:\n{stackTraceStr}')

intents = discord.Intents.default()
intents.presences = True
intents.message_content = True
intents.members = True
bot = Bot(intents = intents)
bot.run(botToken)
