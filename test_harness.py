''' test harness from https://github.com/TatianaParshina/rasa_chatbot/blob/master/test_nlu.py'''
from rasa_nlu.model import Interpreter

# interpreter = Interpreter.load('./models/current/nlu')
model_path = 'C:\\personal\\chatbot_july_2019\\filebot_6\\models\\20191125-204429.tar.gz'
interpreter = Interpreter.load(model_path)

# define function to ask question
def ask_question(text):
    print(interpreter.parse(text))
    
# asking question
ask_question("plot of Luv")
ask_question("plot of Highlander")  
