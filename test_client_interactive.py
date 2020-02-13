import requests
import pandas as pd

'''

sender = input("primer message\n")
# input_text = ['plot of Luv','plot of Goldfinger','plot of GoldenEye']
file_path = 'https://raw.githubusercontent.com/ryanmark1867/chatbot/master/testcases/moviebot_regression_mini.csv'
df = pd.read_csv(file_path)
input_text = df['test_item'].tolist()

bot_message = ""
print("starting...")
for message in input_text:
    print("message is ",message)
          
for message in input_text:
	# message = input("What's your message change?\n")

	# print("Sending message now...")
	

	r = requests.post('http://localhost:5002/webhooks/rest/webhook', json={"sender": sender, "message": message})

	print("Bot answering "+str(message))
	for i in r.json():
		bot_message = i['text']
		print(f"{i['text']}")

'''
sender = input("primer message\n")
bot_message = ""
while bot_message != "Bye":
	message = input("What's your message change?\n")

	print("Sending message now...")
	

	r = requests.post('http://localhost:5002/webhooks/rest/webhook', json={"sender": sender, "message": message})

	print("Bot says, ")
	for i in r.json():
		bot_message = i['text']
		print(f"{i['text']}")
'''


# Test client for interacting with Rasa bot

import requests

sender = input("What is your name?\n")

bot_message = ""
while bot_message != "Bye":
	message = input("What's your message?\n")

	print("Sending message now...")

	r = requests.post('http://localhost:5002/webhooks/rest/webhook', json={"sender": sender, "message": message})

	print("Bot says, ")
	for i in r.json():
		bot_message = i['text']
		print(f"{i['text']}")
'''
