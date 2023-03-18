import os

import dotenv

dotenv.load_dotenv()

debugMode = False
if 'debug' in os.environ:
	debugMode = True
	print('running in DEBUG mode')
else:
	print('running in PRODUCTION mode')

botToken = os.environ['bottoken']
mainServerId = int(os.environ['mainserverid'])