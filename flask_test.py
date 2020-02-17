# tester app to exercised Flask

from flask import Flask, render_template, request
from string import Template
from OpenSSL import SSL
# import classes for exchanging data with dynamic web serving code
from webview_classes import movie_info
from webview_classes import payload_item
import pickle
from rasa.nlu.model import Interpreter
import requests
import json
#import string
#from actions import wv_payload
# import ssl
# context = SSL.Context(SSL.PROTOCOL_TLS)
# client_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
#





# API_ENDPOINT = "http://localhost:5005/webhooks/rest/webhook"
API_ENDPOINT = "http://localhost:5005/webhooks/rest/webhook"
messagePayload = ''
selected_item = ''
selected_category = ''

# BEGIN END STUFF
'''
import traceback
from werkzeug.wsgi import ClosingIterator

class AfterResponse:
    def __init__(self, app=None):
        self.callbacks = []
        if app:
            self.init_app(app)

    def __call__(self, callback):
        self.callbacks.append(callback)
        return callback

    def init_app(self, app):
        # install extension
        app.after_response = self

        # install middleware
        app.wsgi_app = AfterResponseMiddleware(app.wsgi_app, self)

    def flush(self):
        for fn in self.callbacks:
            try:
                fn()
            except Exception:
                traceback.print_exc()

class AfterResponseMiddleware:
    def __init__(self, application, after_response_ext):
        self.application = application
        self.after_response_ext = after_response_ext

    def __call__(self, environ, after_response):
        iterator = self.application(environ, after_response)
        try:
            return ClosingIterator(iterator, [self.after_response_ext.flush])
        except Exception:
            traceback.print_exc()
            return iterator
            


app = Flask("after_response")
AfterResponse(app)

# post close actions 

@app.after_response
def payload_to_rasa():
    
    print("mpayload in payload_to_rasa is "+str(messagePayload))
    print("selected_item is"+str(selected_item))
    print("selected_category is"+str(selected_category))
    r = requests.post(url = API_ENDPOINT, data = messagePayload)

'''
# END APP STUFF

# uncomment this to get back
app = Flask(__name__)

HTML_TEMPLATE = Template("""
<h1>Hello ${file_name}!</h1>

<img src="https://image.tmdb.org/t/p/w342/${file_name}" alt="poster for ${file_name}">

""")

def package_list(key_name,list_in):
    i = 0
    list_out = []
    for element in list_in:
        key_value = list_in[i].strip()
        list_out.append({key_name:key_value})
        i = i+1
    return(list_out)

# @app.route('/animals', methods=['GET', 'POST'])
# @app.route('/')
@app.route('/', methods=['GET', 'POST'])
def homepage():
    #global wv_payload
    # TODO REPLACE THIS HACKY WAY TO GET PAYLOAD
    global messagePayload
    global selected_item
    global selected_category
    print("about to try to show page")
    wv_payload_path = 'wv_payload.pkl'
    with open(wv_payload_path, 'rb') as handle:
        wv_payload = pickle.load(handle)
    '''    
    for wv_payload_index in wv_payload:
        print("here is item "+str(wv_payload_index))
        print("display content is "+str(wv_payload[wv_payload_index].display_content))
        print("display type is "+str(wv_payload[wv_payload_index].display_type))
        print("return type is "+str(wv_payload[wv_payload_index].return_type))
        print("return payload is "+str(wv_payload[wv_payload_index].return_payload))
    '''
    title_display = wv_payload['original_title'].display_content[0]
    print("title_display is "+str(title_display))
    title = {'titlename':str(title_display)}
    year = {'yearname':str(wv_payload['year'].display_content[0])}
    plot = {'plotname':str(wv_payload['overview'].display_content[0])}
    run_time = {'run_timename':str(wv_payload['run_time'].display_content[0])}
    rating = {'ratingname':str(wv_payload['rating'].display_content)}
    poster_url = {'poster_urlname':str(wv_payload['poster_url'].display_content)}
    genre_list = package_list('genre_listname',wv_payload['genre_list'].display_content)
    # genre_list = {'genre_listname':str(wv_payload['genre_list'].display_content)}
    actor_list = package_list('actor_listname',wv_payload['actor_list'].display_content)
    director_list = package_list('director_listname',wv_payload['director_list'].display_content)
    print("ABOUT TO DISPLAY PAGE ")
    selected_item = request.args.get('type')
    selected_category = request.args.get('category')
    print("SELECTED ITEM and CATEGORY"+str(selected_item)+", "+str(selected_category))
    # build query depending on what category was clicked
    #m_payload = "list movies starring John Wayne"
    if selected_category == 'genre':
        m_payload = 'top '+str(selected_item)+' movies'
    if selected_category == 'director':
        m_payload = 'list movies directed by '+str(selected_item)
    if selected_category == 'actor':
        m_payload = 'list movies starring '+str(selected_item)
    #print("mpayload is "+m_payload)
    #messagePayloadPython = {"sender": "default","message": m_payload,"output_channel":"latest"}
    #messagePayload = json.dumps(messagePayloadPython)
    #r = requests.post(url = API_ENDPOINT, data = messagePayload)

    return render_template('home.html',title=title,year = year,plot=plot,run_time=run_time,rating=rating,poster_url=poster_url,genre_list=genre_list,actor_list=actor_list, director_list=director_list)
    print("post return in main func")
    #r = requests.post(url = API_ENDPOINT, data = messagePayload) 
    #return """<h1>Test of dynamic poster display here Feb 1 afternoon</h1>"""
    
@app.route('/about/')
def about():
    return render_template('about.html')

@app.route('/<some_file>')
def some_place_page(some_file):
    return(HTML_TEMPLATE.substitute(file_name=some_file))
    
def test_call(test_text):
    print("from actions.py got "+test_text)

'''    
def read_wv_payload(wv_payload_path):
    global wv_payload
    with open(wv_payload_path, 'rb') as handle:
        wv_payload = pickle.load(handle)
    return()
    '''

'''    
def load_wv_payload(input_wv_payload_list):
    # bring in payload list from actions.py
    global wv_payload
    wv_payload = input_wv_payload_list.copy()
    print("here is wv_payload from inside flask")
    for wv_payload_index in wv_payload:
        print("here is item "+str(wv_payload_index))
        print("display content is "+str(wv_payload[wv_payload_index].display_content))
        print("display type is "+str(wv_payload[wv_payload_index].display_type))
        print("return type is "+str(wv_payload[wv_payload_index].return_type))
        print("return payload is "+str(wv_payload[wv_payload_index].return_payload)) '''
        

'''
@app.route('/')
def index():
    return render_template('summary_template.html')
#    return 'Hello world'
'''

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
    #app.run(host='127.0.0.1', debug=True, ssl_context=context)
    # app.run(ssl_context='adhoc',debug=True, host='0.0.0.0')
    #context = ('C:\personal\chatbot_july_2019\ssl_experiment\server.crt', 'C:\personal\chatbot_july_2019\ssl_experiment\server.key')
    #app.run(ssl_context=context,debug=True, host='0.0.0.0')
