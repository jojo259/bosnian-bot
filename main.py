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
import hashlib
import string

print("init")

class Bot(discord.Client):

	commandPrefix = '.'
	if config.debugMode:
		commandPrefix = ','
	anonWebhookName = 'bosnian-bot-anon'

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.webhook_cache = {}  # Cache will map channel IDs to their webhooks


	async def on_ready(self):
		print(f'logged in as {self.user}')
		self.checkEphemeral.start()
		self.scrambleUsername.start()
		await self.initAnon()
		await self.cache_webhooks()  # Cache webhooks on bot start-up

	async def cache_webhooks(self):
		for guild in self.guilds:
			if guild.id == config.mainServerId:
				for channel in guild.channels:
					print(f'caching webhooks for channel {channel}')
					if isinstance(channel, discord.TextChannel):  # Check if we are dealing with TextChannel which supports webhooks.
						webhooks = await channel.webhooks()
						for webhook in webhooks:
							if webhook.name == self.anonWebhookName:
								self.webhook_cache[channel.id] = webhook  # Cache the webhook for this channel



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

		if curMessage.content[0] == self.commandPrefix:
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
							return

		if config.debugMode:
			return

		if curMessage.channel.category and curMessage.channel.category.name.lower() == 'anon':
			messageContent = curMessage.content
			user_hash = hashlib.sha256(f"{curMessage.author.id}{datetime.datetime.now().strftime('%Y-%m-%d %H')}".encode()).hexdigest()
			user_hashid = ''.join([(string.ascii_uppercase + string.ascii_lowercase + string.digits)[int(user_hash[i:i+2], 16) % 62] for i in range(0, 12, 2)])
			anon_username = f"{user_hashid} anon"

			# Send the message in all anon channels except the user's channel
			print(f'sending anon msg {messageContent}')
			for guild in self.guilds:
				if guild.id == config.mainServerId:
					for channel in guild.channels:
						if channel.category and channel.category.name.lower() == 'anon' and channel.id != curMessage.channel.id:
							await self.send_anon_msg_to_channel(channel, messageContent, anon_username)

			# Delete the original message
			await curMessage.delete()

			# Send the message to the user's channel
			await self.send_anon_msg_to_channel(curMessage.channel, messageContent, anon_username)

	async def send_anon_msg_to_channel(self, channel, content, username):
		webhook = self.webhook_cache.get(channel.id)
		if not webhook:
			print(f'cached webhook not found for {channel.name}, checking if it exists')
			webhooks = await channel.webhooks()
			for existing_webhook in webhooks:
				if existing_webhook.name == self.anonWebhookName:
					webhook = existing_webhook
					break
			if not webhook:
				print(f'webhook not found for {channel.name}, creating')
				webhook = await channel.create_webhook(name=self.anonWebhookName)
			self.webhook_cache[channel.id] = webhook
		print(f'sending anon msg {content} to channel {channel.name}')
		await webhook.send(content, username=username, avatar_url=f'https://robohash.org/{username}?set=set1&bgset=bg1')


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


	async def initAnon(self):

		mainServer = await self.fetch_guild(config.mainServerId)
		existing_category = None
		for curGuild in bot.guilds:
			if curGuild.id == config.mainServerId:
				for curCategory in curGuild.categories:
					if curCategory.name.lower() == 'anon':
						existing_category = curCategory
						break
		if existing_category == None:
			print('Creating "anon" category')
			existing_category = await mainServer.create_category('anon')
		else:
			print('"anon" category already exists')

		for curGuild in bot.guilds:
			if curGuild.id == config.mainServerId:
				for curMember in curGuild.members:
					if not curMember.bot:  # Check if the member is not a bot
						channel_name = f'anon_{curMember.id}'
						# Check if channel already exists

						existing_channel = None
						for curGuild in bot.guilds:
							if curGuild.id == config.mainServerId:
								for curChannel in curGuild.channels:
									if curChannel.name.lower() == channel_name:
										existing_channel = curChannel
										break
						if existing_channel != None:
							print(f'anon Channel for {curMember.id} already exists')
							continue

						overwrites = {
							mainServer.default_role: discord.PermissionOverwrite(read_messages=False),
							curMember: discord.PermissionOverwrite(read_messages=True)
						}
						await mainServer.create_text_channel(channel_name, category=existing_category, overwrites=overwrites)
						print(f'Created anon channel for {curMember.display_name}')

if __name__ == '__main__':
	intents = discord.Intents.default()
	intents.presences = True
	intents.message_content = True
	intents.members = True
	bot = Bot(intents = intents)
	bot.run(config.botToken)
