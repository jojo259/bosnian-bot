import requests
import json

import config

def doRequest(userMessage, systemMessage = 'You are an assistant.'):

	reqMessages = [
		{'role': 'system', 'content': systemMessage},
		{'role': 'user', 'content': userMessage}
	]

	reqHeaders = {
		'Content-type': 'application/json',
		'Authorization': f'Bearer {config.openAiKey}',
	}

	reqBody = {
		'model': config.openAiGptModel,
		'messages': reqMessages,
		'temperature': 1,
		'max_tokens': 1000,
	}

	apiReq = requests.post('https://api.openai.com/v1/chat/completions', headers = reqHeaders, json = reqBody, timeout = 1000)

	try:
		reponseStr = apiReq.json()['choices'][0]['message']['content']
	except Exception as e:
		return apiReq.text

	return reponseStr
