# test harness to exercise the bot with a set of queries read from a file
# assumes that rasa is started with special credentials file:
# 	rasa run -m models --endpoints endpoints.yml --port 5002 --credentials credentials_test.yml
# varieties of test files:
# https://raw.githubusercontent.com/ryanmark1867/chatbot/master/testcases/moviebot_regression.csv - full test set
# https://raw.githubusercontent.com/ryanmark1867/chatbot/master/testcases/moviebot_regression_smoke.csv - 60 rep
# https://raw.githubusercontent.com/ryanmark1867/chatbot/master/testcases/moviebot_regression_mini.csv - sniff test


import requests
import pandas as pd

sender = input("primer message\n")
# input file that is read record by record to exercise the bot
file_path = 'https://raw.githubusercontent.com/ryanmark1867/chatbot/master/testcases/moviebot_regression.csv'
# ingest file into dataframe
df = pd.read_csv(file_path)
# convert single column to list
input_text = df['test_item'].tolist()

bot_message = ""
print("starting...")
# echo the contents of the input file to output
for message in input_text:
    print("message is ",message)
          
# iterate through the contents of the list
for message in input_text:
	# message = input("What's your message change?\n")

	# print("Sending message now...")
	

	r = requests.post('http://localhost:5002/webhooks/rest/webhook', json={"sender": sender, "message": message})

	print("Bot answering "+str(message))
	for i in r.json():
		bot_message = i['text'].encode("utf-8")
		print(f"{i['text']}")


