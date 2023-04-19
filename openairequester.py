import requests
import json

import config

def doRequest(messagesList):

	for message in messagesList:
		if sorted(message.keys()) != sorted(['role', 'content']):
			raise KeyError(f'Wrong keys in messagesList: {message.keys()}')
		for value in message.values():
			if not type(value) == str:
				raise TypeError(f'Wrong type in messagesList values: {type(value)}')

	reqHeaders = {
		'Content-type': 'application/json',
		'Authorization': f'Bearer {config.openAiKey}',
	}

	reqBody = {
		'model': config.openAiGptModel,
		'messages': messagesList,
		'temperature': 1,
		'max_tokens': 250,
	}

	apiReq = requests.post('https://api.openai.com/v1/chat/completions', headers = reqHeaders, json = reqBody, timeout = 1000)

	try:
		reponseStr = apiReq.json()['choices'][0]['message']['content']
	except Exception as e: # todo
		return

	return reponseStr

def constructMessage(role, content):
	return {'role': role, 'content': content}
