import os

import dotenv

dotenv.load_dotenv()

botToken = os.environ['bottoken']
mainServerId = int(os.environ['mainserverid'])