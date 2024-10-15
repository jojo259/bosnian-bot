import requests
import config
import time
import os
import uuid

TXT2IMG_ENDPOINT = 'https://api.novita.ai/v3/async/txt2img'
TASK_RESULT_ENDPOINT = 'https://api.novita.ai/v3/async/task-result'

def generateImage(prompt):
	headers = {
		'Authorization': f'Bearer {config.imageGenApiKey}',
		'Content-Type': 'application/json'
	}
	
	payload = {
		"extra": {
			"response_image_type": "jpeg"
		},
		"request": {
			"prompt": prompt,
			"model_name": "epicrealism_naturalSinRC1VAE_106430.safetensors",
			"negative_prompt": "",
			"width": 1024,
			"height": 1024,
			"image_num": 1,
			"steps": 100,
			"seed": -1,
			"clip_skip": 0,
			"sampler_name": "DPM++ 2S a Karras",
			"guidance_scale": 20
		}
	}
	
	response = requests.post(TXT2IMG_ENDPOINT, headers=headers, json=payload)
	if response.status_code != 200:
		raise Exception(f"Failed to start image generation: {response.text}")
	
	task_id = response.json().get('task_id')

	# Polling for task completion and image retrieval
	while True:
		# Retrieve the result of the image generation
		result_response = requests.get(f"{TASK_RESULT_ENDPOINT}?task_id={task_id}", headers=headers)
		if result_response.status_code != 200:
			raise Exception(f"Failed to retrieve image: {result_response.text}")
		
		result_json = result_response.json()
		print(result_json)
		# Check if the task status is successful
		task_status = result_json['task']['status']
		if task_status == 'TASK_STATUS_SUCCEED':
			# Extract the image URLs from the response
			image_url = result_json['images'][0]['image_url']
			# Fetch and return the image files locally
			return save_image(image_url)
		
		# If task is not completed, wait and retry
		time.sleep(1)

def save_image(image_url):
	# Get the image content
	image_response = requests.get(image_url)
	if image_response.status_code != 200:
		raise Exception(f"Failed to fetch the image: {image_response.text}")
	
	# Save the image locally
	image_filename = f"generated_image_{uuid.uuid4().hex}.jpeg"
	with open(image_filename, 'wb') as img_file:
		img_file.write(image_response.content)
	
	print(f"Image saved as {image_filename}")
	return image_filename
