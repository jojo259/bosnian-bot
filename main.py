import traceback
import discord
import commandslist
import config
from discord.ext import tasks
import asyncio
import datetime
import chatgptreplacer
import random
import util

print("init")

class Bot(discord.Client):

	commandPrefix = '.'
	if config.debugMode:
		commandPrefix = ','


	async def on_ready(self):
		print(f'logged in as {self.user}')
		self.checkEphemeral.start()
		self.scrambleUsername.start()


	async def on_message(self, curMessage):

		if not curMessage.author.bot and not curMessage.content.startswith(self.commandPrefix):
			await chatgptreplacer.checkReplace(self, curMessage)

		if curMessage.channel.id == config.ephemeralChannelId:
			await asyncio.sleep(config.ephemeralChannelMessageLifetimeSeconds)
			print('deleting ephemeral message')
			try:
				await curMessage.delete()
			except discord.errors.NotFound:
				pass
			return

		if curMessage.author == self.user:
			return

		if curMessage.author.bot:
			return

		if curMessage.webhook_id:
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


	@tasks.loop(minutes = 1)
	async def checkEphemeral(self):
		try:
			print('checking ephemeral')
			ephemeralChannel = self.get_channel(config.ephemeralChannelId)
			ephemeralMessages = []
			async for curMessage in ephemeralChannel.history(limit = 100):
				ephemeralMessages.append(curMessage)
			for curMessage in reversed(ephemeralMessages):
				messageTimestamp = curMessage.created_at
				nowTimestamp = datetime.datetime.utcnow().replace(tzinfo = datetime.timezone.utc)
				messageSentAgoSeconds = (nowTimestamp - messageTimestamp).total_seconds()
				if messageSentAgoSeconds > config.ephemeralChannelMessageLifetimeSeconds:
					print('deleting ephemeral message in checkEphemeral')
					try:
						await curMessage.delete()
					except discord.errors.NotFound as e:
						pass
		except Exception as e:
			stackTraceStr = traceback.format_exc()
			print(stackTraceStr)
			ephemeralChannel = self.get_channel(config.ephemeralChannelId)
			await ephemeralChannel.send(stackTraceStr)


	@tasks.loop(seconds = 1)
	async def scrambleUsername(self):
		if random.randint(1, 180) != 1:
			return
		print('scrambling username')
		allMembers = []
		for curGuild in bot.guilds:
			if curGuild.id == config.mainServerId:
				for curMember in curGuild.members:
					allMembers.append(curMember)
		target = random.choice(allMembers)
		switchIndex = random.randint(0, len(target.display_name) - 2)
		newName = target.display_name[:switchIndex]
		newName += target.display_name[switchIndex + 1]
		newName += target.display_name[switchIndex]
		newName += target.display_name[switchIndex + 2:]
		await util.renameMember(target, newName)

if __name__ == '__main__':
	intents = discord.Intents.default()
	intents.presences = True
	intents.message_content = True
	intents.members = True
	bot = Bot(intents = intents)
	bot.run(config.botToken)
