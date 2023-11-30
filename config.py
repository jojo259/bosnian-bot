import os
import dotenv

dotenv.load_dotenv()

ephemeralChannelMessageLifetimeSeconds = 8

debugMode = False
if 'debug' in os.environ:
	debugMode = True
	print('running in DEBUG mode')
else:
	print('running in PRODUCTION mode')

botToken = os.environ['bottoken']
mainServerId = int(os.environ['mainserverid'])
ephemeralChannelId = int(os.environ['ephemeralchannelid'])
openAiKey = os.environ['openaikey']
openAiGptModel = os.environ['openaigptmodel']
openAiGptSpecialModel = os.environ['openaigptspecialmodel']
gptSpecialModelAccessIds = os.environ['gptspecialmodelaccessids'].split(',')
