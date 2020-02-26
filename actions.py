# Custom actions for filebot project

# property of KarmaAI

# common imports

from rasa_sdk import Action, Tracker
#from rasa_sdk import Tracker
#from rasa_core.actions.action import Action
from rasa_sdk.events import SlotSet
from typing import Any, Text, Dict, List
#from rasa_sdk.executor import CollectingDispatcher
from rasa_core_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import pandas as pd
import re
import ast
import json
import copy
import logging
import itertools
import numbers
import decimal
import collections
import string
import requests
import os
from collections import Counter
import yaml
import pickle
#from flask_test import test_call
#from flask_test import read_wv_payload
# import classes for exchanging data with dynamic web serving code
from webview_classes import movie_info
from webview_classes import payload_item
from webview_classes import carousel_tracker




# block to read in key parameters

# get current working directory
current_path = os.getcwd()
print("current directory is: "+current_path)
directory_symbol = "\\"

path_to_yaml = current_path+directory_symbol+"custom_action_config.yml"
print("path_to_yaml "+path_to_yaml)
try: 
    with open (path_to_yaml, 'r') as file:
       config = yaml.safe_load(file)
except Exception as e:
    print('Error reading the config file')

parent_key = config['general']['parent_key']
child_key = config['general']['child_key']
parent_table = config['general']['parent_table']
default_rank = config['general']['default_rank']
default_ranked_col = config['general']['default_rank_col']
# maximum number of FM quick responses
max_qr = config['general']['max_qr']
max_qr_per_row = config['general']['max_qr_per_row']
# switch to serialize dataframes
save_files = config['general']['save_files']
# switch to load from serialized dataframes
saved_files = config['general']['saved_files']
# switch to allow exceptions in try blocks to be exposed
debug_on = config['general']['debug_on']
# limit output to a reasonable number if there are lots
output_limit = config['general']['output_limit']
big_files = config['general']['big_files']
# URL for webview FM root
wv_URL = config['general']['wv_url']
image_path_index = config['general']['image_path_index']
placeholder_image = config['general']['placeholder_image']
carousel_size_per_display = config['general']['carousel_size_per_display']
jahr_zero = config['general']['jahr_zero']
logging_level = config['general']['logging_level']
# detail_mode:
#    type: categorical
#    initial_value: text_list
#    values:
#    - text_list
#    - details

# switch to change the debug level - change to ERROR for faster runs
#logging.getLogger().setLevel(logging.WARNING)
#
#logging = logging.getLogger('myLogger')
#level = logging.getLevelName('INFO')
#Log.setLevel(level)
logging_level_set = logging.WARNING
if logging_level == 'WARNING':
    logging_level_set = logging.WARNING
if logging_level == 'ERROR':
    logging_level_set = logging.ERROR
if logging_level == 'DEBUG':
    logging_level_set = logging.DEBUG
if logging_level == 'INFO':
    logging_level_set = logging.INFO   
logging.getLogger().setLevel(logging_level_set)
logging.warning("logging check")



display_mode = "text_list"
logging.warning("display_mode 1 is: "+display_mode)
wv_payload = {}
# define a persistent dispatcher to display in FM
persistent_dispatcher_set = False
persistent_dispatcher = CollectingDispatcher()

#  test_call("test to other file feb 1, 2020")

# load big file names
path_dict = {}
if big_files:
   file_spec = 'big_files'
else:
   file_spec = 'small_files'
# load path_dict
for file_name in config[file_spec]:
   logging.warning("file_name is: "+file_name)
   logging.warning("file_name value is: "+config[file_spec][file_name])
   path_dict[file_name] = config[file_spec][file_name]


# define the keys used to join parent table (movies) with children tables(keyword_keywords,credits_crew
# credits_cast, movies_spoken_languages, movies_production_companies, movies_production_countries, movies_genres




'''
parent_key = config['general']['parent_key']
child_key = config['general']'movie_id'
parent_table = 'movies'
default_rank = 'popularity'
default_ranked_col = 'original_title'
# maximum number of FM quick responses
max_qr = 13
max_qr_per_row = 3
# switch to serialize dataframes
save_files = False
# switch to load from serialized dataframes
saved_files = True
# switch to allow exceptions in try blocks to be exposed
debug_on = False
# limit output to a reasonable number if there are lots
output_limit = 10
big_files = True
'''

avg_cols = ['rating']
child_tables = ['links','ratings','keywords','movies_genres','movies_production_companies','movies_production_countries','movies_spoken_languages','credits_cast','credits_crew','keywords_keywords']
wv_payload_list = ['poster_url', 'original_title', 'year', 'rating','run_time','genre_list','director_list','actor_list','crew_dict','overview'] #list of all the elements in the webview outbound payload




class Condition:
   def __init__(self,value_list,d_table):
      self.value = value_list
      self.table = d_table
   
   

def json_check(string, placeholder): 
   ''' input string and placeholder JSON. If string parses as valid Python, return result of literal_eval.
   Otherwise, return placeholder string'''
   try:
      testarray = ast.literal_eval(string)
   except ValueError as e:
      return placeholder
   return string

# define paths for movie dataset files

'''
path_dict = {}
if big_files:
   path_dict['links'] = 'C:\personal\chatbot_july_2019\datasets\links.csv'
   path_dict['movies'] = 'C:\personal\chatbot_july_2019\datasets\movies_metadata.csv'
   # had to rename because \r means something!
   path_dict['ratings'] = 'C:\personal\chatbot_july_2019\datasets\mratings.csv'
   path_dict['credits'] = 'C:\personal\chatbot_july_2019\datasets\credits.csv'
   path_dict['keywords'] = 'C:\personal\chatbot_july_2019\datasets\keywords.csv'
else:
   path_dict['links'] = 'https://raw.githubusercontent.com/ryanmark1867/chatbot/master/datasets/links_small.csv'
   path_dict['movies'] = 'https://raw.githubusercontent.com/ryanmark1867/chatbot/master/datasets/movies_metadata_small.csv'
   path_dict['ratings'] = 'https://raw.githubusercontent.com/ryanmark1867/chatbot/master/datasets/ratings_small.csv'
   path_dict['credits'] = 'https://raw.githubusercontent.com/ryanmark1867/chatbot/master/datasets/credits_small.csv'
   path_dict['keywords'] = 'https://raw.githubusercontent.com/ryanmark1867/chatbot/master/datasets/keywords_small.csv'
'''
image_path = 'https://image.tmdb.org/t/p/w500'
image_path_dict = {}
image_path_dict["small"] = 'https://image.tmdb.org/t/p/w92' # 92x138
image_path_dict["medium"] = 'https://image.tmdb.org/t/p/w342' # 342x513
image_path_dict["big"] = 'https://image.tmdb.org/t/p/w500' # 500x750

persistent_carousel_dict = {}
# switch of whether there is an active carousel
carousel_active = False
carousel_size = 0

media_dict = {}
media_dict['poster'] = 'image'
media_dict['video'] = 'video'
media_dict['trailer'] = 'video'

# placeholders used to clean up files with missing JSON values so that they can have literal_eval processing done on them
crew_placeholder = str([{'credit_id': '52fe4ab0c3a368484e161d3d', 'department': 'Directing', 'gender': 0, 'id': 1080311, 'job': 'Director', 'name': 'Sandip Ray', 'profile_path': None}])
cast_placeholder = str([{'cast_id': 0, 'character': '', 'credit_id': '53be47fb0e0a26158f003788', 'gender': 2, 'id': 1894, 'name': 'Scott Caan', 'order': 1, 'profile_path': '/kvUKf9HCaqUtgj7XuKZOvN66MOT.jpg'}, {'cast_id': 1, 'character': '', 'credit_id': '53be48030e0a2615760039f8', 'gender': 0, 'id': 1339926, 'name': 'Lee Nashold', 'order': 2, 'profile_path': None}, {'cast_id': 2, 'character': '', 'credit_id': '53be480a0e0a26158f00378a', 'gender': 2, 'id': 24362, 'name': 'Kevin Michael Richardson', 'order': 3, 'profile_path': '/9dMOW2CFRrlDkNzeXVGMJfASupM.jpg'}, {'cast_id': 3, 'character': '', 'credit_id': '53be48110e0a2615820038b6', 'gender': 2, 'id': 3085, 'name': 'James Caan', 'order': 4, 'profile_path': '/g4bxNXWft1jLZX8gKk4G6ypkTUf.jpg'}, {'cast_id': 4, 'character': '', 'credit_id': '53be48180e0a26157c003802', 'gender': 0, 'id': 53646, 'name': 'Missy Crider', 'order': 5, 'profile_path': '/xkFq4Ye3yz6R5EaBBLb6bY5IDjs.jpg'}, {'cast_id': 5, 'character': '', 'credit_id': '53be481f0e0a2615820038b9', 'gender': 2, 'id': 827, 'name': 'Elliott Gould', 'order': 6, 'profile_path': '/bo5jSwWyFRsKVAkELT9n7AKQqMk.jpg'}, {'cast_id': 6, 'character': '', 'credit_id': '53be48260e0a26157c003804', 'gender': 2, 'id': 62032, 'name': 'Duane Davis', 'order': 7, 'profile_path': '/t9tcFEEbffaD64VZdsc0qwnPnr9.jpg'}])

# define columns in each file that are JSON formatted and need to be ast.literal_eval processed
json_dict = {}
json_dict['links'] = []
json_dict['movies'] = ['genres','production_companies','production_countries','spoken_languages',]
json_dict['ratings'] = []
json_dict['credits'] = ['cast','crew']
'''
score_sample = {}
score_sample['hour'] = np.array([18])
score_sample['Route'] = np.array([0])
score_sample['daym'] = np.array([21])
score_sample['month'] = np.array([0])
score_sample['year'] = np.array([5])
score_sample['Direction'] = np.array([1])
score_sample['day'] = np.array([1])
'''
json_dict['keywords'] = ['keywords']


# map various strings to correct column names
# define synonyms (TODO see how to move at least a subset of these to Rasa level so they don't have to be maintained at Python layer)
slot_map = dict.fromkeys(['movies','movie name','movie','title','original_title'],'original_title')
slot_map.update(dict.fromkeys(['plot','plot summary','plot statement','overview','story','Story','Plot'],'overview'))
slot_map.update(dict.fromkeys(['release date','release_date'],'release_date'))
slot_map.update(dict.fromkeys(['year','when','date','Date','Year'],'year'))
slot_map.update(dict.fromkeys(['French'],'fr'))
slot_map.update(dict.fromkeys(['English'],'en'))
slot_map.update(dict.fromkeys(['German'],'de'))
slot_map.update(dict.fromkeys(['budget'],'budget'))
slot_map.update(dict.fromkeys(['revenue'],'revenue'))
slot_map.update(dict.fromkeys(['director','Director'],'Director'))
slot_map.update(dict.fromkeys(['producer','Producer'],'Producer'))
slot_map.update(dict.fromkeys(['costume_design','Costume_Design'],'Costume_Design'))
slot_map.update(dict.fromkeys(['editor','Editor'],'Editor'))
slot_map.update(dict.fromkeys(['original_language'],'original_language'))
slot_map.update(dict.fromkeys(['science fiction','Science Fiction','Science_Fiction'],'Science Fiction'))
slot_map.update(dict.fromkeys(['funny','comedy','Comedy'],'Comedy'))
slot_map.update(dict.fromkeys(['rating','Rating'],'rating'))
# slot_map.update(dict.fromkeys(['popularity','rating'],'rating'))
slot_map.update(dict.fromkeys(['cast','castmember','cast_name','actor','actors','actress','actresses'], 'cast_name'))
slot_map.update(dict.fromkeys(['crew','crewmember','crew_name'], 'crew_name'))
slot_map.update(dict.fromkeys(['characters','character','character_name'], 'character'))
slot_map.update(dict.fromkeys(['language','movies_language_name'], 'movies_language_name'))
slot_map.update(dict.fromkeys(['genre','genre_name'], 'genre_name'))
slot_map.update(dict.fromkeys(['keyword','keyword_name'], 'keyword_name'))
slot_map.update(dict.fromkeys(['ascending'], 'ascending'))
slot_map.update(dict.fromkeys(['Costume_Design'], 'Costume_Design'))


# define the subset of slots that can be condition columns:
# TODO confirm whether this list should contain exclusively slot names from rasa (e.g. no "original_title")
# TODO determine if possible to generate this list automatically instead of hand creating it
slot_condition_columns = ["original_language","original_title","movie","Rating","rating","character","Costume Design","story","Editor","editor","plot","director","Director","Producer","genre","budget","overview","keyword","keyword_name","revenue","cast_name","crew_name","genre_name","year"]

def add_id_to_dict(dict_list,id_name,id):
   ''' for list of dictionaries dict_list, add the entry "id_name":id to each dictionary in the list'''
   str2 = "dict_list is"+str(dict_list)
   str3 = "id_name "+str(id_name)+" id "+str(id)
   logging.debug(str2)
   logging.debug(str3)
   for dict in dict_list:
      dict[id_name] = id
   return dict_list


# load df_dict dictionary with dataframes corresponding to the datasets
# if saved_files, load from pickled dataframes created previously by this code block
# if save_files, save the 

df_dict = {}
for file in path_dict:
   print("about to create df for ",file)
   if saved_files:
      # load pickled file corresponding to dataframes for the dataset files
      # pickled files for derived dataframes loaded below
      logging.warning("loading df from pickle file for : "+str(file))
      if big_files:
         big_folder = "bigpickle\\"
         read_handle = big_folder+str(file)
         logging.warning("read_handle is: "+str(read_handle))
      else:
         small_folder = "smallpickle\\"
         read_handle =  small_folder+str(file)
         read_handle = big_folder+str(file)
         logging.warning("read_handle is: "+str(read_handle))
      df_dict[file] = pd.read_pickle(str(read_handle))
   else:
      logging.warning("path is : "+str(path_dict[file]))
      df_dict[file] = pd.read_csv(path_dict[file])
      # manually cleaned up credits file - TODO make this real so input more resiliant
      for cols in json_dict[file]:
         logging.warning("about to ast.literal_eval "+cols)
         # apply tranformation to render JSON strings from the CSV file into Python structures
         # need to do this or operations cannot be performed on the structures (e.g. check_keyword_dict)
         df_dict[file][cols] = df_dict[file][cols].apply(lambda x: ast.literal_eval(x))
         # add the id all the dictionaries in the JSON format columns
         logging.warning("about to add ids to dictionaries in "+cols+" for file "+file)
         logging.warning(str(df_dict[file][cols].loc[[1]]))
         df_dict[file][cols] = df_dict[file].apply(lambda x: add_id_to_dict(x[cols],'movie_id',x['id']),axis=1)
         # create a new handle for the new dataframe
         if big_files:
            big_folder = "bigpickle\\"
            new_handle = big_folder+str(file)+"_"+str(cols)
         else:
            small_folder = "smallpickle\\"
            new_handle =  small_folder+str(file)+"_"+str(cols)
            
         new_handle = str(file)+"_"+str(cols)
         logging.warning("new handle is "+new_handle)
         nh_list = df_dict[file][cols].values
         # consolidate list of lists of dictionaries into a single list of dictionaries
         nh_list_single = list(itertools.chain.from_iterable(nh_list))
         # define new dataframe with distinct columns for each range in the original df's JSON column
         # and add new dataframe to df_dict
         df_dict[new_handle] = pd.DataFrame(nh_list_single)
         logging.warning("post new_handle col add: "+str(df_dict[new_handle].head()))
      # need to replace id column 
        
# load up the generated dataframes that came from JSON
if saved_files:
   for file in path_dict:
      for cols in json_dict[file]:
         # load pickled files corresponding to dataframes generated from JSON columns in original dataset
         if big_files:
            big_folder = "bigpickle\\"
            read_handle = big_folder+str(file)+"_"+str(cols)
            logging.warning("JSON read_handle is: "+str(read_handle))
         else:
            small_folder = "smallpickle\\"
            read_handle =  small_folder+str(file)+"_"+str(cols)
            logging.warning("JSON read_handle is: "+str(read_handle))
         new_handle =  str(file)+"_"+str(cols)
         logging.warning("loading df from pickle file for : "+new_handle)
         df_dict[new_handle] = pd.read_pickle(str(read_handle))
if save_files:
   # have to go through df_dict again in a separate loop since new df_dict entries added in the above loop
   # save all the dataframes in the df_dict dictionary in separate pickle files
   for file in df_dict:
      df_dict[file].to_pickle(str(file))


# load the schema dictionary with "table":[colum1,column2...] 
#
def load_schema_dict(df_dict):
   schema_dict = {}
   for file in df_dict:
      schema_dict[file] = list(df_dict[file])
      #logging.warning("schema_dict for "+file+" is "+str(schema_dict[file]))
      #logging.warning("size of df for "+file+" is "+str(len(df_dict[file].index)))
   return(schema_dict)

'''
RESULT:'popularity'
links is ['movieId', 'imdbId', 'tmdbId']
movies is ['adult', 'belongs_to_collection', 'budget', 'genres', 'homepage', 'id', 'imdb_id', 'original_language', 'original_title', 'overview', 'popularity', 'poster_path', 'production_companies', 'production_countries', 'release_date', 'revenue', 'runtime', 'spoken_languages', 'status', 'tagline', 'title', 'video', 'vote_average', 'vote_count']
ratings is ['userId', 'movieId', 'rating', 'timestamp']
credits is ['cast', 'crew', 'id']
keywords is ['id', 'keywords']
movies_genres is ['id', 'name', 'movie_id']
movies_production_companies is ['name', 'id', 'movie_id']
movies_production_countries is ['iso_3166_1', 'name', 'movie_id']
movies_spoken_languages is ['iso_639_1', 'name', 'movie_id']
credits_cast is ['cast_id', 'character', 'credit_id', 'gender', 'id', 'name', 'order', 'profile_path', 'movie_id']
credits_crew is ['credit_id', 'department', 'gender', 'id', 'job', 'name', 'profile_path', 'movie_id']
keywords_keywords is ['id', 'name', 'movie_id']
'''

# define category_table_dict dictionary of dataframes indexed by category name
category_table_dict = {}
category_table_dict['genre'] = df_dict['movies_genres']
category_table_dict['production_company'] = df_dict['movies_production_companies']
category_table_dict['production_country'] = df_dict['movies_production_countries']
category_table_dict['spoken_language'] = df_dict['movies_spoken_languages']
category_table_name = {}
category_table_name['genre'] = 'genre'
category_table_name['production_company'] = 'movies_production_company'
category_table_name['production_country'] = 'movies_production_country'
category_table_name['spoken_language'] = 'movies_language'

# rename some columns to avoid duplicates
df_dict['movies_genres'].rename({'name':'genre_name'},axis=1,inplace=True)
df_dict['movies_production_companies'].rename({'name':'movies_production_company_name'},axis=1,inplace=True)
df_dict['movies_production_countries'].rename({'name':'movies_production_country_name'},axis=1,inplace=True)
df_dict['movies_spoken_languages'].rename({'name':'movies_language_name'},axis=1,inplace=True)
df_dict['credits_cast'].rename({'name':'cast_name'},axis=1,inplace=True)
df_dict['credits_crew'].rename({'name':'crew_name'},axis=1,inplace=True)
df_dict['keywords_keywords'].rename({'name':'keyword_name'},axis=1,inplace=True)
# there two have no JSON columns so need to explicitly rename key column to child_key
df_dict['ratings'].rename({'movieId':child_key},axis=1,inplace=True)
df_dict['links'].rename({'movieId':child_key},axis=1,inplace=True)
# generate separate 'year' column from 'release_date'
df_dict['movies']['year'] = df_dict['movies']['release_date'].str[:4]
# deal with NaN values that mess up some MVP queries
df_dict['movies']['year'] = df_dict['movies']['year'].fillna('1990')






# define distinct dataframes for each profession in the credits_crew df
def create_crew_by_job_dfs(credits_df,df_dict):
   ''' create distinct tables for each job in credits_crew '''
   # df.name.unique()
   job_list = credits_df.job.unique()
   for job_name in job_list:
      # for each unique job, create
      job_name_uscore = job_name.replace(" ","_")
      new_handle = "credits_crew_"+job_name_uscore
      #logging.warning("job new handle "+str(new_handle))
      df_dict[new_handle] = credits_df[credits_df['job'] == job_name]
      df_dict[new_handle].rename({'crew_name':job_name_uscore},axis=1,inplace=True)
          
   return(df_dict)



# main prep code block
df_dict = create_crew_by_job_dfs(df_dict['credits_crew'],df_dict)
movie_schema = load_schema_dict(df_dict)

import requests

headers = {
    'Content-Type': 'application/json'
}

params = (
    ('access_token', "EAAKrBDkZCQtgBAHnWHM5q24XbgXJQrwKcr4WAt1FE8OBWI7vZCS3jBBVX5BXm0XmBLjrNgEyU4Glwdhd49B7wAKLtYgMZAb9PikX6JZCMk4FrXl6hSUPbRdkSUJOitjpiPl6BA2Szx0oAJrE5A94oxGSAMxTNsecRnq9tzMGJQZDZD"
   ),
)

data = {  "greeting":
   [
      {      "locale":"default",
             "text":"Hello!"     },
      {     "locale":"en_US", "text":"Timeless apparel for the masses."
            }
      ]
   }

# response = requests.post('https://graph.facebook.com/v2.6/me/messenger_profile', headers=headers, params=params, data=data)

# response = requests.post('https://graph.facebook.com/v2.6/me/messenger_profile?access_token=EAAKrBDkZCQtgBAHnWHM5q24XbgXJQrwKcr4WAt1FE8OBWI7vZCS3jBBVX5BXm0XmBLjrNgEyU4Glwdhd49B7wAKLtYgMZAb9PikX6JZCMk4FrXl6hSUPbRdkSUJOitjpiPl6BA2Szx0oAJrE5A94oxGSAMxTNsecRnq9tzMGJQZDZD', headers=headers, data=data)

#response = requests.post('https://graph.facebook.com/v2.6/me/messenger_profile', headers=headers,params = params, data=data)
#                         ?access_token=EAAKrBDkZCQtgBAHnWHM5q24XbgXJQrwKcr4WAt1FE8OBWI7vZCS3jBBVX5BXm0XmBLjrNgEyU4Glwdhd49B7wAKLtYgMZAb9PikX6JZC
#                         Mk4FrXl6hSUPbRdkSUJOitjpiPl6BA2Szx0oAJrE5A94oxGSAMxTNsecRnq9tzMGJQZDZD', headers=headers, data=data)


# logging.warning("response: "+str(response))



# df.to_csv(file_name, sep='\t')
# csv_file_name = 'C:\personal\chatbot_july_2019\df_to_csv\movies_genres.csv'
# logging.warning("about to write genre to csv")
# df_dict['movies_genres'].to_csv(csv_file_name)

logging.warning("BEFORE credits_cast col names "+str(list(df_dict['credits_cast'].columns.values)))
logging.warning("BEFORE movies col names "+str(list(df_dict['movies'].columns.values)))

df_dict['credits_cast']['movie_id2'] = df_dict['credits_cast']['movie_id']
df_dict['movies']['id2'] = df_dict['movies']['id']

df_dict['credits_cast'] = df_dict['credits_cast'].set_index('movie_id2')
df_dict['credits_cast'] = df_dict['credits_cast'].sort_index()
print("AFTER credits_cast col names "+str(list(df_dict['credits_cast'].columns.values)))
df_dict['movies'] = df_dict['movies'].set_index('id2')
df_dict['movies'] = df_dict['movies'].sort_index()
print("AFTER movies col names "+str(list(df_dict['movies'].columns.values)))

def get_image_path(image_file):
   # TODO replace with code that gets the actual base path
   return(image_path+image_file)



# classes for individual custom actions triggered by Rasa
      
class ActionFileColumns(Action):
   """ return the column names for a file """
   def name(self) -> Text:
      return "action_file_columns"
   def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
      csv_url = tracker.get_slot('file_name')
      df=pd.read_csv(csv_url)
      result = list(df)
      dispatcher.utter_message("Here is the list of column names for file:")
      dispatcher.utter_message(csv_url)
      for i in range(len(result)):
          dispatcher.utter_message(result[i]+" ")
      return []
      


class ActionFileRow(Action):
   """ return the values in a specific row """
   def name(self) -> Text:
      return "action_file_row"
   def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
      csv_url = tracker.get_slot('file_name')
      csv_row = int(tracker.get_slot('row_number'))
      df=pd.read_csv(csv_url)
      # get raw values from dataframe
      result = df.values
      header_output = "contents for row "+str(csv_row)+" are:"
      dispatcher.utter_message(header_output)
      #
      # convert all elements of the row to strings (dispather.utter_message will only output strings)
      str_array = [str(i) for i in result[csv_row]]
      # concatenate all the elements of the string cast arrage
      one_line_output = ", ".join(str_array)
      dispatcher.utter_message(one_line_output)
      #for i in range(len(result[csv_row])):
      #   dispatcher.utter_message(str(result[csv_row][i]))
      return []

class ActionFirstNRows(Action):
   """ return the values of the first n rows """
   def name(self) -> Text:
      return "action_first_n_rows"
   def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
      csv_url = tracker.get_slot('file_name')
      csv_row_range = int(tracker.get_slot('row_range'))
      df=pd.read_csv(csv_url)
      # get raw values from dataframe
      result = df.values
      header_output = "last "+str(csv_row_range)+" rows are:"
      dispatcher.utter_message(header_output)
      for j in range (csv_row_range):
         str_array = [str(i) for i in result[j]]
         one_line_output = ", ".join(str_array)
         dispatcher.utter_message(one_line_output)
      return []

   
class ActionLastNRows(Action):
   """return the values of the last n rows"""
   def name(self) -> Text:
      return "action_last_n_rows"
   def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
      csv_url = tracker.get_slot('file_name')
      csv_row_range = int(tracker.get_slot('row_range'))
      df=pd.read_csv(csv_url)
      number_rows = len(df.index)
      # get raw values from dataframe
      result = df.values
      header_output = "last "+str(csv_row_range)+" rows are:"
      dispatcher.utter_message(header_output)
      # iterate through the last n rows
      for j in range (number_rows-csv_row_range,number_rows):
         str_array = [str(i) for i in result[j]]
         one_line_output = ", ".join(str_array)
         dispatcher.utter_message(one_line_output)
      return []

class ActionRankColByOtherCol(Action):
   """return the values of the last n rows"""
   def name(self) -> Text:
      return "action_rank_col_by_other_col"
   def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
      slot_dict = tracker.current_slot_values()
      for slot_entry in slot_dict:
         dispatcher.utter_message(str(slot_entry))
         dispatcher.utter_message(str(slot_dict[slot_entry]))
      return []
   
class action_condition_by_year(Action):
   """return the values scoped by year"""
   def name(self) -> Text:
      return "action_condition_by_year"
   def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
      slot_dict = tracker.current_slot_values()
      #for slot_entry in slot_dict:
      #   dispatcher.utter_message(str(slot_entry))
      #   dispatcher.utter_message(str(slot_dict[slot_entry]))
      ranked_col = tracker.get_slot("ranked_col")
      year = tracker.get_slot("year")
      top_bottom = tracker.get_slot("top_bottom")
      genre = tracker.get_slot("genre")
      if top_bottom == 'top':
         ascend_direction = False
      else:
         ascend_direction = True
      csv_row = int(tracker.get_slot('row_number'))
      sort_col = tracker.get_slot("sort_col")
      if genre == None:
         dispatcher.utter_message("genre is None")
      str1 = "COMMENT: getting "+ str(ranked_col) + " for year "+str(year)
      dispatcher.utter_message(str1)
      df=df_dict['movies']
      ranked_col = slot_map[ranked_col]
      result = (df[df['release_date'].str[:4] == year].sort_values(by = [sort_col],ascending=ascend_direction))[ranked_col]
      limiter = int(csv_row)
      i = 0
      str2 = "COMMENT: number of elements to show is "+str(limiter)
      dispatcher.utter_message(str2)
      for item in result:
         dispatcher.utter_message(str(item))
         i = i+1
         if i >= limiter:
            break
      dispatcher.utter_message("COMMENT: end of transmission")
      return [SlotSet("ranked_col",None),SlotSet("movie",None),SlotSet("media",None),SlotSet("rank_axis",None),SlotSet("keyword",None),SlotSet("year",None),SlotSet("genre",None),SlotSet("plot",None),SlotSet("Director",None),SlotSet("cast_name",None)]

    




# TODO: instead of the complex multifaceted structure of various dictionaries and lists, encapsulate in a class
# to make the updates simpler and to avoid losing track of what's a list vs. dictionary

# helper function for refactored main class action_condition_by_movie

def execute_query (condition_col, condition_table, condition_value, condition_operator,top_bottom,ascending_descending,ranked_col, returned_values):
   """ perform query on specified table """
   return_values = condition_table[condition_table[condition_col] == condition_value][ranked_col]
   return(return_values)

def get_table(column_list,schema):
   """ return the table that contains the given column in the given schema dictionary"""
   table_dict = {}
   logging.warning("FEB 25 column_list in get_table is: "+str(column_list))
   # logging.warning("FEB 25 column_list in schema is: "+str(column_list))
   for table in schema:
      #logging.warning("FEB 25 get_table table is: "+str(table))
      for column in column_list:
         #logging.warning("FEB 25 get_table column is: "+str(column))
         if column in schema[table]:
            logging.warning("FEB 25 get_table got table "+str(table)+" for column: "+str(column))
            table_dict[column] = table
   logging.warning("FEB 25 table_dict is"+str(table_dict))
   return(table_dict)

def get_condition_columns(slot_dict):
   ''' given a slot dictionary, return dictionary of condition columns whose slots are filled in '''
   condition_dict = {}
   for slot in slot_dict:
      logging.warning("in gcc slot is "+str(slot))
      logging.warning("in gcc slot_dict[slot] "+str(slot_dict[slot]))
      # check  if slot is a candidate for condition column and that it's not empty
      if not(slot_dict[slot] is None) and (slot in slot_condition_columns):
         logging.warning("get_condition_columns found "+str(slot))
         condition_dict[slot]= slot_dict[slot]
         #condition_col.append(slot)
   return(condition_dict)

def same_table(condition_table, ranked_table):
   ''' return true if both lists have exactly one element, and this element which is the same. Otherwise return false '''
   # check a single unique value in each list
   if ((len((Counter(condition_table).keys())) == 1) and (len((Counter(ranked_table).keys())) == 1)):
      # check to see if unique values identical
      return(collections.Counter(set(condition_table))== collections.Counter(set(ranked_table)))
   else:
      return(False)
   

def prep_slot_dict(slot_dict):
   ''' iterate through slot dictionary mapping slot keys and values from Rasa settings to what's required for schema '''
   for slot_entry in slot_dict:
      logging.warning("in slot_entry loop slot_entry is: "+str(slot_entry))
      logging.warning("in slot_entry loop slot_dict[slot_entry] is: "+str(slot_dict[slot_entry]))
      if slot_entry in slot_condition_columns:
         logging.warning("in slot_condition_columns for slot_entry: "+str(slot_entry))
         # syntax to replace key value
         slot_dict[slot_map[slot_entry]] = slot_dict.pop(slot_entry)
         logging.warning("in slot_condition_columns new key set for "+str(slot_map[slot_entry]))
      logging.warning("after "+str(slot_entry))
   length = len(slot_dict["ranked_col"])
   i = 0
   while i < length:
      # iterate through entries in ranked_col list
      logging.warning("in slot_entry loop ranked_col slot_entry is: "+str(i))
      slot_dict["ranked_col"][i] = slot_map[slot_dict["ranked_col"][i]]
      logging.warning("in slot_entry loop ranked_col slot_entry is: "+str(slot_dict["ranked_col"][i]))
      i = i+1
   return(slot_dict)

def get_results_same_table(result,condition_dict,condition_table,slot_dict):
   logging.warning("same_table condition_table "+str(condition_table))
   first_same = True
   # iterate through conditions keeping all columns
   for condition in condition_dict:
      logging.warning("in single table condition loop for condition "+str(condition))
      if first_same:
         # first time through loop set base_df
         base_df = df_dict[condition_table[condition]]
         first_same = False
      base_df = base_df[base_df[condition] == condition_dict[condition]]
   result = base_df[slot_dict["ranked_col"]]
   return(result)


    


def get_selection_column_list(condition_table_list,ranked_table_list):
   ''' get list of columns to pull in final result'''
   return()

def get_condition_columns_to_pull(child_key, ranked_table, condition_table):
   ''' return the ranked columns that are in the condition_table
   child_key: column that is always pulled from condition_table for use to join with main table
   ranked_table: dictionary of form  {'original_title': 'movies', 'character': 'credits_cast'}
   condition_table: name of the table that corresponds with the condition that is being applied: e.g. 'movies', 'credits_cast' '''
   # list(mydict.keys())[list(mydict.values()).index(16)]
   column_list = [child_key]
   if condition_table in ranked_table.values():
      # reverse lookup the key in ranked_table that corresponds with the value condition_table and append to column_list
      column_list.append(list(ranked_table.keys())[list(ranked_table.values()).index(condition_table)])
   return(column_list)

def output_result(dispatcher,result,row_range,tracker):
   ''' common output to bot interface and logger '''
   global display_mode
   global persistent_dispatcher
   global persistent_dispatcher_set
   i = 0
   # if the range to print is None, use overall default. Otherwise use range
   logging.warning("display_mode 2 is: "+display_mode)
   # TODO symptom where if row_range in query matches value in training sample output format is strange. Workaround now in training.
   if row_range == None:
      print_limit = output_limit
   else:
      print_limit = int(row_range)
   # check if the result df contains a column (like rating) that needs to be averaged
   avg_set = list(set(list(result)) & set(avg_cols))
   # prep for details view
   qr_count = 0
   qr_list = []
   col_list = []
   # determine if dispatcher has been saved yet, and if not, save it. If it has been saved, use the saved one 
   '''
   if not(persistent_dispatcher_set):
    logging.warning("EYECATCHER - SETTING PERSISTEN_DISPATCHER_SET")
    persistent_dispatcher_set = True
    persistent_dispatcher = copy.deepcopy(dispatcher)
   else:
    logging.warning("EYECATCHER - SETTING DISPATCHER TO PERSISTENT")
    dispatcher = persistent_dispatcher 
   '''
   if not avg_set:
      # no average columns to calculate
      for index, row in result.iterrows():
         str_row = ""
         str_row_log = ""
         i = i+1
         if i > print_limit:
            break
         for col in result.columns:
            # don't output ID columns for final bot rendering
            if (col != parent_key and col != child_key):
               str_raw = str(row[col])
               str_row = str_row+" "+str(row[col])+"\t"
               # add this col to list of columns
               col_list.append(col)
            str_row_log = str_row_log+" "+str(row[col])+"\t"
         logging.warning("pre display_mode output "+str_row_log)
         # check whether a simple output or details with linkable buttons
         if display_mode == 'text_list':
            logging.warning("ABOUT TO TRY TO DISPLAY display_mode text_list")
            # FEB 16 change to force display in FM
            tracker.events[1]['input_channel'] = "facebook"
            tracker_value = tracker.get_latest_input_channel()
            logging.warning("IN DISPLAY input_channel FEB 17b "+str(tracker_value))
            # dispatcher.utter_custom_json(message1)
            # "message":{
            #"text":"hello, world!"
            #}
            #message1 = {
            #    "output_channel":"facebook",
            #    "message": str_row
            #}
            #dispatcher.utter_custom_json(message1)
            dispatcher.utter_message(str_row)
         else:
            # build query that the qr will trigger
            # TODO get better than this hacky way to get year included
            payload_text = "show details for "+str_raw
            logging.warning("payload_text is "+payload_text)
            t_year = df_dict['movies'][df_dict['movies']['original_title']==str_raw]
            title_year = t_year.iloc[0]['year']
            title_text = str_raw+" ("+str(title_year)+")"
            logging.warning("title_text is "+title_text)
            # build qr entry
            qr_list.append({"content_type":"text",
                       "payload": payload_text,
                       "title": title_text})
            qr_count = qr_count+1
            if qr_count >= max_qr:
               break
      # if qrs being output, build remainder of json and send
      if display_mode == 'details':
         details_text = tracker.get_slot('genre_name')+", good choice!  Here are some highly rated movies."
         details_message = {               
                      "text": details_text,
                      "quick_replies": qr_list
                      }
         logging.warning("details_message is "+str(details_message))
         dispatcher.utter_custom_json(details_message)
         display_mode = "text_list"
   else:
      # need to print average of columns
      for col in avg_set:
         result["avg"]=result[col].astype(float)
         logging.warning(result["avg"].mean())
         dispatcher.utter_message(str(round(result["avg"].mean(),2)))
   
   return()

'''
      # build list of quick responses
      i = 0
      qr_list = []
      for value in category_values:
         payload_text = "top "+value+" movies"
         logging.warning("payload_text is "+payload_text)
         qr_list.append({"content_type":"text",
                       "payload": payload_text,
                       "title": value})
         i = i+1
         if i >= max_qr:
            break
      list_category_text = "select "+category
      list_category_message = {               
                      "text": list_category_text,
                      "quick_replies": qr_list
                      }
      logging.warning("list_category_message is "+str(list_category_message))
      dispatcher.utter_custom_json(list_category_message)  
      # set the display mode to detailed so that the results are clickable
      return[SlotSet('detail_mode','details')]
'''

def get_key_column(table):
   ''' return the key column for the input table'''
   # TODO want a more sophisticated approach for general schemas
   if table == parent_table:
      return_key = parent_key
   else:
      return_key = child_key
   return(return_key)

def prep_compare(string_in):
   ''' perform case, punctuation removal required to have valid comparison of slot values from Rasa and values from the database'''
   string_out = string_in.lower().translate(str.maketrans(string.punctuation, ' '*len(string.punctuation)))
   return(re.sub(' +', ' ', string_out))
   
   
def generate_result(slot_dict,condition_dict,condition_table,ranked_table,dispatcher):
   ''' main function to compile and execute query to iteratively select and join to get result set'''
   # start with a fresh dataframe
   result = pd.DataFrame()
   try:
      logging.warning("RC PRE LOOP 3 slot_dict[ranked_col] is"+str(slot_dict["ranked_col"]))
      if same_table(list(condition_table.values()),list(ranked_table.values())):
         logging.warning("same_table condition_table "+str(condition_table))
         first_same = True
         # iterate through conditions keeping all columns
         for condition in condition_dict:
            logging.warning("in single table condition loop for condition "+str(condition))
            logging.warning("in single table condition loop for condition_table[condition] "+str(condition_table[condition]))
            if first_same:
               # first time through loop set base_df
               base_df = df_dict[condition_table[condition]]
               first_same = False
            logging.warning("in single table condition loop for condition_dict[condition] "+str(condition_dict[condition]))
            # TODO: need to handle list of conditions properly - currently OR for a list
            if isinstance(condition_dict[condition], list):
               logging.warning("in single table condition loop got a list for base_df[condition]  "+str(base_df[condition]))
               # nov 30 base_df = base_df[(base_df[condition].str.lower()).isin(map(lambda x:x.lower(),condition_dict[condition]))]
               base_df = base_df[(base_df[condition].apply(lambda x: prep_compare(x))).isin(map(lambda x:x.lower(),condition_dict[condition]))]
            else:
               #base_df = base_df[base_df[condition] == str(condition_dict[condition])]
               logging.warning("in single table condition loop not a list for base_df[condition]  "+str(base_df[condition]))
               # base_df = base_df[base_df[condition].str.contains(str(condition_dict[condition]))]
               temp_df = base_df[base_df[condition].apply(lambda x: prep_compare(x))== str(prep_compare(condition_dict[condition]))]
               if len(temp_df) == 0:
                  # try fuzzy match
                  logging.warning("trying fuzzy match for  "+str(base_df[condition]))
                  base_df = base_df[(base_df[condition].apply(lambda x: prep_compare(x))).str.contains(str(prep_compare(condition_dict[condition])).lower())]
                  # base_df = base_df[prep_compare(condition_dict[condition]) in base_df[condition].apply(lambda x: prep_compare(x))]
               else:
                  base_df = temp_df


               
         logging.warning("RESULT IS "+str(base_df[slot_dict["ranked_col"]]))
         result_col_list = slot_dict["ranked_col"]
         # check if the rank_axis column needs to be ncluded
         if slot_dict["rank_axis"] != None:
            result_col_list.append(slot_dict["rank_axis"])
         result = base_df[result_col_list]
      else:
         logging.warning("different condition_table"+str(condition_table)+" ranked_table "+str(ranked_table))
         # TODO: eventually want to consider a class to replace all the various dictionaries
         # but for now, just make the condition and ranked table containers dictionaries indexed by slot/column
         # rather than lists
         # condition and rank in different tables
         first_different = True
         child_key_df_dict = {}
         for condition in condition_table:
            # check if condition value is a list
            # for this condition, build the list of columns to pull from the child table
            condition_columns_to_pull = get_condition_columns_to_pull(get_key_column(condition_table[condition]), ranked_table, condition_table[condition])
            if isinstance(condition_dict[condition], list):
               # TODO complete logic for dealing with conditions that are lists
               logging.warning("condition_dict is a list "+str(condition))
               logging.warning("condition_dict prepped is "+str(prep_compare(condition)))
               sub_condition_df_dict = {}
               # iterate through each element in the condition value list getting a df of matching child keys
               for sub_condition in condition_dict[condition]:
                  logging.warning("sub_condition is "+str(sub_condition))
                  # sub_condition_df_dict[sub_condition] = df_dict[condition_table[condition]][df_dict[condition_table[condition]][condition].str.contains(sub_condition)][condition_columns_to_pull]
                  sub_condition_df_dict[sub_condition] = df_dict[condition_table[condition]][df_dict[condition_table[condition]][condition].apply(lambda x: prep_compare(x))==str(prep_compare(sub_condition))][condition_columns_to_pull]
                  if len(sub_condition_df_dict[sub_condition]) == 0:
                     # if no exact match try for fuzzy match
                     sub_condition_df_dict[sub_condition] = df_dict[condition_table[condition]][(df_dict[condition_table[condition]][condition].apply(lambda x: prep_compare(x))).str.contains(str(prep_compare(sub_condition)))][condition_columns_to_pull]
                     #poster_file = df_dict['movies'][(df_dict['movies']['original_title'].str.lower()).str.contains(slot_dict['original_title'].lower())]['poster_path']

               
                  logging.warning("sub_condition_df_dict[sub_condition] len is "+str(len(sub_condition_df_dict[sub_condition])))
                  logging.warning("sub_condition_df_dict[sub_condition] is "+str(sub_condition_df_dict[sub_condition]))
               logging.warning("sub_condition_df_dict len is "+str(len(sub_condition_df_dict)))
               # merge the child key dfs to get a single df containing the intersection of child keys
               first_sub_condition = True
               for sub_condition in sub_condition_df_dict:
                  logging.warning("sub_condition in merge loop is "+str(sub_condition))
                  if first_sub_condition:
                     first_sub_condition = False
                     child_key_df_dict[condition] = sub_condition_df_dict[sub_condition]
                  else:
                     child_key_df_dict[condition] = pd.merge(child_key_df_dict[condition],sub_condition_df_dict[sub_condition],on=child_key,how='inner')
               logging.warning("sub_condition child_key_df_dict[condition] len is "+str(len(child_key_df_dict[condition])))
               logging.warning("number of rows in child_key_df "+str(len(child_key_df_dict[condition].index)))
            else:
               # condition is not a list
               logging.warning("in multi table condition loop for not list condition "+str(condition))
               # build df that just contains child_keys for this
               # child_key_df_dict[condition] = df_dict[condition_table[condition]][df_dict[condition_table[condition]][condition] == condition_dict[condition]][condition_columns_to_pull]
               child_key_df_dict[condition] = df_dict[condition_table[condition]][(df_dict[condition_table[condition]][condition]).apply(lambda x: prep_compare(x)) == str(prep_compare(condition_dict[condition]))][condition_columns_to_pull]
               if len(child_key_df_dict[condition]) == 0:
                  child_key_df_dict[condition] = df_dict[condition_table[condition]][(df_dict[condition_table[condition]][condition]).apply(lambda x: prep_compare(x)).str.contains(str(prep_compare(condition_dict[condition])))][condition_columns_to_pull]
               
               logging.warning("number of rows in child_key_df "+str(len(child_key_df_dict[condition].index)))
         for condition in condition_table:
            # iteratively merge child key tables
            if first_different:
               logging.warning("got first different "+str(condition))
               logging.warning("number of rows in child_key_df second loop "+str(len(child_key_df_dict[condition].index)))               
               result_child_merge = child_key_df_dict[condition]
               first_different = False
            else:
               result_child_merge = pd.merge(result_child_merge,child_key_df_dict[condition],on=child_key,how='inner')
         # now merge with parent table
         logging.warning("RC PRE LOOP 2 slot_dict[ranked_col] is"+str(slot_dict["ranked_col"]))
         logging.warning("number of rows in child_key_df "+str(len(result_child_merge.index)))
         logging.warning("type of result_child_merge is "+str(type(type(result_child_merge))))
         for item_c in result_child_merge:
            logging.warning("item is "+str(item_c))
         first_final = True
         #
         logging.warning("slot_dict[ranked_col] is "+str(slot_dict["ranked_col"]))
         logging.warning("parent_key is "+str(parent_key))
         result_col_list = slot_dict["ranked_col"].copy()
         # result_col_list.append(parent_key)
         if slot_dict["rank_axis"] != None:
            result_col_list.append(slot_dict["rank_axis"])
         logging.warning("result_col_list is "+str(result_col_list))
         logging.warning("left table is "+str(ranked_table[slot_dict["ranked_col"][0]]))
         # define left join key
         if child_key in list(result_child_merge):
            left_key = child_key
         else:
            left_key = parent_key
         logging.warning("left table is "+str(ranked_table[slot_dict["ranked_col"][0]]))
         
         left_merge_col = slot_dict["ranked_col"][0]
         left_merge_df = df_dict[ranked_table[left_merge_col]]
         # iterate through rank columns, joining with result_child_merge
         result = result_child_merge
         logging.warning("RC PRE LOOP left table RESULT is"+str(result))
         logging.warning("RC PRE LOOP iterating through "+str(slot_dict["ranked_col"]))
         # put a test in here to check for just the rank_col that aren't also condition cols (see code in get_condition_columns_to_pull function)
         for rank_col in slot_dict["ranked_col"]:
            # if this column has already been pulled then don't do it again
            # TODO more elegant way of doing this
            if rank_col in condition_columns_to_pull:
               logging.warning("RC LOOP got CONTINUE with "+str(rank_col))
               continue
            logging.warning("RC LOOP: rank_col is "+str(rank_col))
            right_merge_df = df_dict[ranked_table[rank_col]]
            # use child_key by default
            logging.warning("RC LOOP: right cols are "+str(list(right_merge_df)))
            logging.warning("RC LOOP: child key is "+str(child_key))
            if child_key in list(right_merge_df):
               logging.warning("RC LOOP: got child "+str(child_key))
               right_key = child_key
            else:
               logging.warning("RC LOOP: got parent key is "+str(parent_key))
               right_key = parent_key
            logging.warning("RC LOOP: left_key is "+str(left_key))
            logging.warning("RC LOOP: right_key is "+str(right_key))
            logging.warning("RC LOOP: left cols are "+str(list(result)))
            logging.warning("RC LOOP: right cols are "+str(list(right_merge_df)))
            # take subset of cols on right to avoid dup cols
                      
            # TODO find more elegant way to get delta between two lists
            cols_to_use = list(right_merge_df)
            logging.warning("RC LOOP: cols_to_use before is "+str(cols_to_use))
            for col in list(right_merge_df):
               if col in list(result) and col != right_key:
                  cols_to_use.remove(col)
            logging.warning("RC LOOP: cols_to_use before after "+str(cols_to_use))
            logging.warning("RC LOOP PRE MERGE number of rows in result "+str(len(result.index)))
            logging.warning("RC LOOP PRE MERGE number of rows in right_merge_df "+str(len(right_merge_df.index)))
            result = pd.merge(result,right_merge_df[cols_to_use],left_on=left_key,right_on=right_key,how='inner')
            #
         # take the required subset of columns                          
         logging.warning("AFTER RC LOOP: result cols are "+str(list(result)))
         logging.warning("AFTER RC LOOP: result_col_list are "+str(result_col_list))
         result = result[result_col_list]                         
         #result = pd.merge(left_merge_df,result_child_merge,left_on=left_key,right_on=right_key,how='inner')[result_col_list]
         logging.warning("about to leave generate_result")   
   except Exception as e:
      if debug_on:
         raise
      logging.warning("exception generated "+str(e))
      dispatcher.utter_message("query generated error - please continue with next query")
   else:
      logging.warning("exception not generated")
   return(result)

class action_condition_by_movie_ordered(Action):
   """return the values from one or more tables and order output results"""
   def name(self) -> Text:
      return "action_condition_by_movie_ordered"
   def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
      logging.warning("IN CONDITION BY MOVIE ORDERED")
      try:
         # get dictionary of slot values
         slot_dict = {}
         slot_dict = tracker.current_slot_values()
          # set defaults
         if slot_dict["rank_axis"] == None:
            slot_dict["rank_axis"] = default_rank
         if slot_dict["ascending_descending"] == None:
            slot_dict["ascending_descending"] = "descending"
         if slot_dict["ranked_col"] == None:
            slot_dict["ranked_col"] = [default_ranked_col]
         # apply mappings in slot_dict from Rasa to table schema
         slot_dict = prep_slot_dict(slot_dict)
         condition_dict = {}
        
         condition_dict = get_condition_columns(slot_dict)
         
         # get_table expects a list of columns as its first arg, so just take keys from condition_dict dictionary
         logging.warning("ABOUT TO GET CONDITION TABLE ")
         condition_table = get_table(list(condition_dict.keys()),movie_schema)
         logging.warning("ABOUT TO GET RANKED TABLE ")
         # if no ranking column is specified, assume default
      
         ranked_table = get_table(slot_dict["ranked_col"],movie_schema)
         logging.warning("ABOUT TO GET SORT TABLE ")
         sort_table = get_table([slot_dict["rank_axis"]],movie_schema)
         logging.warning("condition_dict is "+str(condition_dict))
         logging.warning("condition_table is "+str(condition_table))
         logging.warning("ranked_col is "+str(slot_dict["ranked_col"]))
         logging.warning("ranked_table is "+str(ranked_table))
      
         logging.warning("sort_col is "+str(slot_dict["rank_axis"]))
         logging.warning("sort_table is "+str(sort_table))
         # work through condition columns to get preliminary result
         result_pre_sort = generate_result(slot_dict,condition_dict,condition_table,ranked_table,dispatcher)
         logging.warning("past result_pre_sort")
         logging.warning(" result_pre_sort type"+str(type(result_pre_sort)))
         logging.warning(" df_dict[sort_table] type"+str(type(df_dict[sort_table[slot_dict["rank_axis"]]])))
         # check the direction of sort
         if slot_dict["ascending_descending"] == "ascending":
            sort_direction_ascending = True
         else:
            sort_direction_ascending = False
         result = result_pre_sort.sort_values(by = [slot_dict["rank_axis"]],ascending=sort_direction_ascending)[slot_dict["ranked_col"]]
         if len(result) > 0:
            output_result(dispatcher,result,slot_dict["row_range"],tracker)
         else:
            dispatcher.utter_message("empty result - please try another query")
      except Exception as e:
         if debug_on:
            raise
         logging.warning("exception generated "+str(e))
         dispatcher.utter_message("query generated error - please continue with next query")
      logging.warning("COMMENT: end of transmission FM")
      
      #return [SlotSet("ranked_col",None),SlotSet("character",None),SlotSet("movie",None),SlotSet("rank_axis",None),SlotSet("keyword",None),SlotSet("year",None),SlotSet("genre",None),SlotSet("plot",None),SlotSet("Director",None),SlotSet("cast_name",None)]
      return[SlotSet('budget',None),SlotSet('cast_name',None),SlotSet('character',None),SlotSet('condition_col',None),SlotSet('condition_operator',None),SlotSet('condition_val',None),SlotSet('Costume_Design',None),SlotSet('Director',None),SlotSet('Editor',None),SlotSet('file_name',None),SlotSet('genre',None),SlotSet('keyword',None),SlotSet('language',None),SlotSet('media',None),SlotSet('original_title',None),	SlotSet('original_language',None),SlotSet('plot',None),SlotSet('Producer',None),SlotSet('rank_axis',None),SlotSet('ranked_col',None),SlotSet('revenue',None),SlotSet('row_number',None),SlotSet('row_range',None),SlotSet('sort_col',None),SlotSet('top_bottom',None),SlotSet('year',None),SlotSet('ascending_descending',None)]



# new condition_by_movie class:
#     - JSON columns processed in separate dataframes rather than native
#     - code generalized to handle a wide variety of queries


class action_condition_by_movie(Action):
    """return the values from one or more tables"""
    def name(self) -> Text:
        return "action_condition_by_movie"
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        tracker_value = tracker.get_latest_input_channel()
        logging.warning("IN CONDITION BY MOVIE TRACKER_VALUE "+str(tracker_value))
        # get dictionary of slot values
        try:
            slot_dict = {}
            slot_dict = tracker.current_slot_values()
            # apply mappings in slot_dict from Rasa to table schema
            slot_dict = prep_slot_dict(slot_dict)
            condition_dict = {}
            condition_dict = get_condition_columns(slot_dict)
            # get_table expects a list of columns as its first arg, so just take keys from condition_dict dictionary
            logging.warning("ABOUT TO GET CONDITION TABLE ")
            condition_table = get_table(list(condition_dict.keys()),movie_schema)
            logging.warning("FEB 25 condition_dict before is "+str(condition_dict))
            logging.warning("FEB 25 condition_table before is "+str(condition_table))
            logging.warning("ABOUT TO GET RANKED TABLE ")
            ranked_table = get_table(slot_dict["ranked_col"],movie_schema)
            logging.warning("FEB 25 condition_dict after is "+str(condition_dict))
            logging.warning("FEB 25 condition_table after is "+str(condition_table))
            logging.warning("ranked_cod is "+str(slot_dict["ranked_col"]))
            logging.warning("ranked_table is "+str(ranked_table))
            # call major logic to get results - keep this common for all actions that require filtering and joining of tables
            result = generate_result(slot_dict,condition_dict,condition_table,ranked_table,dispatcher)      
            logging.warning("number of rows in result "+str(len(result)))
            # output result
            logging.warning("result is "+str(result))
            if len(result) > 0:
                output_result(dispatcher,result,slot_dict["row_range"],tracker)
            else:
                dispatcher.utter_message("empty result - please try another query")
        except Exception as e:
            if debug_on:
                raise
            logging.warning("exception generated "+str(e))
            dispatcher.utter_message("query generated error - please continue with next query")
        logging.warning("COMMENT: end of transmission")
      
        # TODO more elegant way to clear out used slots
        #return [SlotSet("ranked_col",None),SlotSet("character",None),SlotSet("movie",None),SlotSet("rank_axis",None),SlotSet("keyword",None),SlotSet("year",None),SlotSet("genre",None),SlotSet("plot",None),SlotSet("Director",None),SlotSet("cast_name",None)]
        return[SlotSet('budget',None),SlotSet('cast_name',None),SlotSet('character',None),SlotSet('condition_col',None),SlotSet('condition_operator',None),SlotSet('condition_val',None),SlotSet('Costume_Design',None),SlotSet('Director',None),SlotSet('Editor',None),SlotSet('file_name',None),SlotSet('genre',None),SlotSet('keyword',None),SlotSet('language',None),SlotSet('media',None),SlotSet('original_title',None),	SlotSet('original_language',None),SlotSet('plot',None),SlotSet('Producer',None),SlotSet('rank_axis',None),SlotSet('ranked_col',None),SlotSet('revenue',None),SlotSet('row_number',None),SlotSet('row_range',None),SlotSet('sort_col',None), SlotSet('top_bottom',None),SlotSet('year',None),SlotSet('ascending_descending',None)]


class action_clear_slots(Action):
   """debug action from active chat to flush slots after failed query - otherwise bad slot values hang around and mess up subsequent queries"""
   def name(self) -> Text:
      return "action_clear_slots"
   def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
      logging.warning("IN CLEAR SLOTS")
      return[SlotSet('budget',None),SlotSet('cast_name',None),SlotSet('character',None),SlotSet('condition_col',None),SlotSet('condition_operator',None),SlotSet('condition_val',None),SlotSet('Costume_Design',None),SlotSet('Director',None),SlotSet('Editor',None),SlotSet('file_name',None),SlotSet('genre',None),SlotSet('keyword',None),SlotSet('language',None),SlotSet('media',None),SlotSet('original_title',None),	SlotSet('original_language',None),SlotSet('plot',None),SlotSet('Producer',None),SlotSet('rank_axis',None),SlotSet('ranked_col',None),SlotSet('revenue',None),SlotSet('row_number',None),SlotSet('row_range',None),SlotSet('sort_col',None),SlotSet('top_bottom',None),SlotSet('year',None),SlotSet('ascending_descending',None)]

     
      '''
      EXAMPLE OF CONDITION LIST
      - condition_dict is {'cast_name': ['Sean Connery']}
      - condition_table is ['credits_cast']
      - ranked_cod is original_title
      - ranked_table is ['movies']

      EXAMPLE OF CONDITION NOT A LIST
      condition_dict is {'original_title': 'Toy Story'}
      condition_table is ['movies']
      ranked_cod is budget
      ranked_table is ['movies']
      '''
      
def get_wv_payload(key_slot, key_value):
    ''' for the key_slot with key_value, assemble the payload to be displayed in webview. returns dictionary of payload_item objects'''
    #wv_payload_list = ['poster_url', 'original_title', 'year', 'rating','run_time','genre_list','director_list','actor_list','crew_dict','overview'] #list of all the elements in the webview outbound payload
    #wv_payload_dict = {} # dictionary of payload items sent to webview rendering
    '''def __init__(display_content,display_type,return_type, return_payload):
        self.display_content = display_content # what gets shown in webview
        self.display_type = display_type # how it gets shown: text, link, image
        self.return_type = return_type # where action occurs if this item is selected: fm (close wv and return payload back to Facebook Messenger), wv (stay in wv and take action there)
        self.return_payload = return_payload # what gets sent back if this display item gets selected'''
    # TODO post demo 1 get a more elegant way to get all the required keys
    # base_df = base_df[(base_df[condition].apply(lambda x: prep_compare(x))).isin(map(lambda x:x.lower(),condition_dict[condition]))]
    movie_id_list = df_dict['movies'][(df_dict['movies'][key_slot].apply(lambda x: prep_compare(x)))==key_value]['id'].tolist()
    logging.warning("movie_id_list is"+str(movie_id_list))
    movie_id_value = movie_id_list[0]
    wv_payload_list = {}
    poster_path_list = df_dict['movies'][df_dict['movies']['id']==movie_id_value]['poster_path'].tolist()
    logging.warning("poster_path_list is"+str(poster_path_list))
    wv_payload_list['poster_url'] = payload_item(image_path_dict[image_path_index]+"/"+poster_path_list[0],'image',None,None)
    wv_payload_list['original_title']= payload_item(df_dict['movies'][df_dict['movies']['id']==movie_id_value]['original_title'].tolist(),'text',None,None)
    wv_payload_list['year']= payload_item(df_dict['movies'][df_dict['movies']['id']==movie_id_value]['year'].tolist(),'text',None,None)
    # TODO replace placeholder - need to find a way to extract rating more efficiently
    wv_payload_list['rating']= payload_item('PLACEHOLDER','text',None,None)
    wv_payload_list['run_time'] = payload_item(df_dict['movies'][df_dict['movies']['id']==movie_id_value]['runtime'].tolist(),'text',None,None)
    wv_payload_list['genre_list'] = payload_item(df_dict['movies_genres'][df_dict['movies_genres']['movie_id']==movie_id_value]['genre_name'].tolist(),'text',None,None)
    # TODO need to define behaviour for click on director or actor links
    dir_list = df_dict['credits_crew_Director'][df_dict['credits_crew_Director']['movie_id']==movie_id_value]['Director'].tolist()
    wv_payload_list['director_list'] = payload_item(dir_list,'link','fm','show movies directed by ')
    wv_payload_list['actor_list'] = payload_item(df_dict['credits_cast'][df_dict['credits_cast']['movie_id']==movie_id_value]['cast_name'].tolist(),'link','fm','show movies starring ')
    wv_payload_list['overview'] = payload_item(df_dict['movies'][df_dict['movies']['id']==movie_id_value]['overview'].tolist(),'text',None,None)
    return(wv_payload_list)
    
def load_wv_payload(wv_payload):
    ''' make payload available to flask - tactically via a pickle file'''
    wv_payload_path = 'wv_payload.pkl'
    with open(wv_payload_path, 'wb') as handle:
        pickle.dump(wv_payload, handle, protocol=pickle.HIGHEST_PROTOCOL)
    # trigger reading on the flask eng
    # read_wv_payload(wv_payload_path)
    return()
    
def get_carousel_payload(key_slot, key_value):
    ''' for the key_slot with key_value, assemble the payload to be displayed in carousel for demo step 5. return payload list'''
    # TODO post demo 1, replace this hacky approach and combine with getting the payload for webview
    # TODO hierarchy of dictionaries (used to simplify serialization to JSON) with class definition - ideally adapt wv_payload class
    # dictionary containing entire carousel payload, including array of dictionaries of movies
    # get all movie IDs for movies where this cast member is listed
    # only profile path uniquely identifies individual - cast_id doesn't
    logging.warning("carousel key_slot is"+str(key_slot))
    logging.warning("carousel key_value is"+str(key_value))
    # movie_id_list = df_dict['credits_cast'][(df_dict['credits_cast'][key_slot].apply(lambda x: prep_compare(x)))==key_value]['movie_id'].tolist()
    logging.warning("TIMING before cast_name search")
    movie_id_df = df_dict['credits_cast'][(df_dict['credits_cast'][key_slot].apply(lambda x: prep_compare(x)))==key_value][['movie_id','profile_path']]
    cast_picture_url_list = movie_id_df['profile_path'].tolist()
    # join movie_id df with movie df to get year and sort increasing by year
    logging.warning("TIMING before movie_id movie merge")
    movie_id_df_year = pd.merge(movie_id_df,df_dict['movies'],left_index=True, right_index=True,how='left').sort_values(['year'])[['movie_id','year']]
    # movie_id_df_year = movie_id_df.join(df_dict['movies']).sort_values(['year'])[['movie_id','year']]
    # take only movies above the base year
    movie_id_list = movie_id_df_year[(pd.to_numeric(movie_id_df_year['year']) > jahr_zero)]['movie_id'].tolist()
    # get list of related movie_ids sorted by release year
    # movie_id_df = (df_dict['credits_cast'][(df_dict['credits_cast'][key_slot].apply(lambda x: prep_compare(x)))==key_value]['movie_id'year']).sort_values(['year'])
    # movie_id_list = (movie_id_df.drop('year',axis=1)).tolist()
    # cast_id_list = df_dict['credits_cast'][(df_dict['credits_cast'][key_slot].apply(lambda x: prep_compare(x)))==key_value]['cast_id'].tolist()
    # credits_cast is ['cast_id', 'character', 'credit_id', 'gender', 'id', 'cast_name', 'order', 'profile_path', 'movie_id']
    cast_pict = True
    carousel_dict = {}
    carousel_dict["cast_name"] = key_value
    carousel_dict["movie_list"] = []
    logging.warning("TIMING before cast_picture search merge")
    #cast_picture_url_list = df_dict['credits_cast'][(df_dict['credits_cast'][key_slot].apply(lambda x: prep_compare(x)))==key_value]['profile_path'].tolist()
    if len(cast_picture_url_list) <= 0:
        cast_picture_url_list.append(placeholder_image)
        cast_pict = False
     
    carousel_dict["cast_picture_url"] = cast_picture_url_list[0]
    # key_slot_prepped = (df_dict['credits_cast'][key_slot].apply(lambda x: prep_compare(x)))
    carousel_size = len(movie_id_list)
    logging.warning("TIMING before payload build loop")
    logging.warning("FEB 25 carousel_size is "+str(carousel_size))
    for movie_id_value in movie_id_list:
        movie_carousel_dict = {}
        #logging.warning("carousel movie_id is"+str(movie_id_value))
        # original_title_list = df_dict['movies'][df_dict['movies']['id']==movie_id_value]['original_title'].tolist()
        original_title_df = df_dict['movies'][df_dict['movies']['id']==movie_id_value][['original_title','year','poster_path']]
        original_title_list = original_title_df['original_title'].tolist()
        year_list = original_title_df['year'].tolist()
        poster_path_list = original_title_df['poster_path'].tolist()
        # check for corrupted entries and skip
        if len(original_title_list) <= 0:
            continue
        #logging.warning("carousel poster_path_list is"+str(original_title_list))
        movie_carousel_dict["original_title"] = original_title_list[0]
        # year_list = df_dict['movies'][df_dict['movies']['id']==movie_id_value]['year'].tolist()
        movie_carousel_dict["year"] = year_list[0]
        # movie_id_list = df_dict['movies'][(df_dict['movies'][key_slot].apply(lambda x: prep_compare(x)))==key_value]['id'].tolist()
        if cast_pict:
            #use cast_pict as an index if it exists
            movie_carousel_dict["character"] = df_dict['credits_cast'][(df_dict['credits_cast']['movie_id']==movie_id_value) & (df_dict['credits_cast']['profile_path']==cast_picture_url_list[0])]['character'].tolist()
        else:
            movie_carousel_dict["character"] = df_dict['credits_cast'][(df_dict['credits_cast']['movie_id']==movie_id_value) & ((df_dict['credits_cast'][key_slot].apply(lambda x: prep_compare(x)))==key_value)]['character'].tolist()
        #logging.warning("carousel character_list is"+str(movie_carousel_dict["character"]))
        # poster_path_list = df_dict['movies'][df_dict['movies']['id']==movie_id_value]['poster_path'].tolist()
        #logging.warning("carousel poster_path_list is"+str(poster_path_list))
        movie_carousel_dict["poster_path"] = image_path_dict[image_path_index]+poster_path_list[0]
        carousel_dict["movie_list"].append(movie_carousel_dict.copy())
    # preserver the carousel_dict to show left and right 
    # global persistent_carousel_dict = carousel_dict
    return(carousel_dict,carousel_size)
    
def build_carousel_json(carousel_payload, carousel_size,start_index,end_index):
    ''' build the required JSON as a string then use ast.literal_eval(s) to convert to Python object suitable for  dispatcher.utter_custom_json'''
    # output_string = prefix_string+<cell_string>+<between_cell_string>+suffix_string
    prefix_string = '{"attachment":{"type":"template","payload":{"template_type":"generic","elements":['
    target_URL = wv_URL
    between_cell_string = ','
    suffix_string = ']}}}'
    cell_string = ''
    # set flags for whether there will be forward and back buttons
    if start_index == 0:
        no_before = True
    else:
        no_before = False
    if end_index <= carousel_size:
        no_next = False
    else:
        no_next = True
    extra_button_string = " "
    for i in range(start_index, end_index):
        cell_string_title = '{ "title":"'+carousel_payload["movie_list"][i]["original_title"]+'('+carousel_payload["movie_list"][i]["year"]+')",'
        cell_string_image = '"image_url":"'+carousel_payload["movie_list"][i]["poster_path"]+'",'
        if len(carousel_payload["movie_list"][i]['character']) == 0:
            sub_title_str = "not named"
        else: 
            sub_title_str = str(carousel_payload["movie_list"][i]["character"]).strip('[]')
        cell_string_subtitle = '"subtitle":"'+sub_title_str+'",'
        # deal with the prev/next button
        logging.warning("BUILD-CAROUSEL-JSON start_index i is "+str(i))
        logging.warning("BUILD-CAROUSEL-JSON start_index "+str(start_index)+"no_before"+str(no_before)+" end_index "+str(end_index)+" no_next "+str(no_next))
        if i == start_index and no_before == False:
            extra_button_string_payload = 'scroll command for '+carousel_payload['cast_name']+' start '+str(int(start_index)-carousel_size_per_display)+' end '+str(int(start_index))
            logging.warning("BUILD-CAROUSEL-JSON prev extra_button_string_payload "+extra_button_string_payload)
            extra_button_string = ',{"type": "postback","payload":"'+extra_button_string_payload+'","title": "Previous"}'
        else:
            if i == (end_index-1) and no_next == False:
                extra_button_string_payload = 'scroll command for '+carousel_payload['cast_name']+' start '+str(end_index)+' end '+str(int(end_index)+carousel_size_per_display)
                logging.warning("BUILD-CAROUSEL-JSON next extra_button_string_payload "+extra_button_string_payload)
                extra_button_string = ',{"type": "postback","payload":"'+extra_button_string_payload+'","title": "Next"}'
        #cell_mid_boilerplate = '"buttons":[ {"type":"web_url","url":"'+target_URL+'",'+'"title":"Movie Details","messenger_extensions": "true","webview_height_ratio": "tall"}]}'
        cell_mid_boilerplate = '"buttons":[ {"type":"web_url","url":"'+target_URL+'",'+'"title":"Movie Details","messenger_extensions": "true","webview_height_ratio": "tall"}'+extra_button_string+']}'
        cell_string = cell_string+cell_string_title+cell_string_image+cell_string_subtitle+cell_mid_boilerplate
        if i < end_index:
            cell_string = cell_string+','
        logging.warning("BUILD-CAROUSEL-JSON cell_string "+cell_string)
    overall_string = prefix_string +cell_string+suffix_string
    logging.warning("BUILD-CAROUSEL-JSON overall_string "+overall_string)
    payload_for_FM = ast.literal_eval(overall_string)         
        
    
    '''
    main_title_str = movie_dict["original_title"]+"("+movie_dict["year"]+")"
            main_title.append(main_title_str)
            if len(movie_dict["character"]) == 0:
                sub_title_str = "not named"
            else: 
                # str(my_list3).strip('[]')
                sub_title_str = str(movie_dict["character"]).strip('[]')
            sub_title.append(sub_title_str)
            img.append(movie_dict["poster_path"])
    
    
    one_cell_string = '{
                   "attachment":{
                     "type":"template",
                     "payload":{
                       "template_type":"generic",
                       "elements":[
                          {'
                           "title":main_title[0],
                           "image_url":img[0],
                           "subtitle":sub_title[0],
                           "buttons":[
                          {
                           "type":"web_url",
                           "url":target_URL,
                           "title":"Movie Details",
                           "messenger_extensions": "true",
                           "webview_height_ratio": "tall"
                          }]},
                          {
                           "title":main_title[1],
                           "image_url":img[1],
                           "subtitle":sub_title[1],
                           "buttons":[
                          {
                           "type":"web_url",
                           "url":target_URL,
                           "title":"Movie Details",
                           "messenger_extensions": "true",
                           "webview_height_ratio": "tall"
                          }]}                            
                        ]      
                      }
                    }
                  }
                  '''
    return(payload_for_FM)

class action_scroll_carousel(Action):
   """special demo action to scroll carousel that has already been displayed by click on webview page"""
   def name(self) -> Text:
      return "action_scroll_carousel"
   def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
    logging.warning("COMMENT - ACTION_SCROLL_CAROUSEL")
    scroll_start = tracker.get_slot('scroll_start')
    scroll_end = tracker.get_slot('scroll_end')
    logging.warning("scroll_start "+str(scroll_start))
    logging.warning("scroll_end "+str(scroll_end))
    message6 = build_carousel_json(carousel_payload, carousel_size,int(scroll_start),int(scroll_end))
 
    try:
        if len(carousel_payload["movie_list"]) > 0:
            dispatcher.utter_custom_json(message6)
        else:
            dispatcher.utter_message("COMMENT - empty - no carousel")
    except:
         if debug_on:
            raise
         dispatcher.utter_message("carousel failed - please try another query")
    return[SlotSet('budget',None),SlotSet('cast_name',None),SlotSet('character',None),SlotSet('condition_col',None),SlotSet('condition_operator',None),SlotSet('condition_val',None),SlotSet('Costume_Design',None),SlotSet('Director',None),SlotSet('Editor',None),SlotSet('file_name',None),SlotSet('genre',None),SlotSet('keyword',None),SlotSet('language',None),SlotSet('media',None),SlotSet('original_title',None),	SlotSet('original_language',None),SlotSet('plot',None),SlotSet('Producer',None),SlotSet('rank_axis',None),SlotSet('ranked_col',None),SlotSet('revenue',None),SlotSet('row_number',None),SlotSet('row_range',None),SlotSet('sort_col',None),SlotSet('top_bottom',None),SlotSet('year',None),SlotSet('ascending_descending',None)]

    
class action_show_carousel(Action):
   """special demo action to show carousel with details picked from webview click"""
   def name(self) -> Text:
      return "action_show_carousel"
   def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
    # the column of the key will be in condition_col and the key itself will be in the slot indicated by condition_col
    # TODO replace hardcoding of condition_col with something more intelligent
    logging.warning("IN ACTION_SHOW_CAROUSEL")
    condition_col = 'cast_name'
    raw_key = tracker.get_slot(condition_col)
    # for slot in 
    logging.warning("carousel condition_col is"+str(condition_col))
    logging.warning("carousel raw_key is"+str(raw_key))
    global carousel_payload
    global carousel_size
    carousel_payload, carousel_size = get_carousel_payload('cast_name',raw_key[0])
    left_index = 0
    if carousel_size <= carousel_size_per_display:
        right_index = carousel_size
    else:
        right_index = carousel_size_per_display
    current_carousel = carousel_tracker(left_index,right_index,carousel_size,carousel_payload)
    ''' given an actor, show a carousel with the posters for all the actor's movies, in text the movie title, date, character name
    '''
    logging.warning("TIMING about to build carousel")
    message6 = build_carousel_json(carousel_payload, carousel_size,0,2)
    main_title = []
    sub_title = []
    poster_path = []
    img = []
    try:
        if len(carousel_payload["movie_list"]) > 0:
            slot_dict = tracker.current_slot_values()
            dispatcher.utter_custom_json(message6)
        else:
            dispatcher.utter_message("COMMENT - empty - no carousel")
    except:
         if debug_on:
            raise
         dispatcher.utter_message("carousel failed - please try another query")
    return[SlotSet('budget',None),SlotSet('cast_name',None),SlotSet('character',None),SlotSet('condition_col',None),SlotSet('condition_operator',None),SlotSet('condition_val',None),SlotSet('Costume_Design',None),SlotSet('Director',None),SlotSet('Editor',None),SlotSet('file_name',None),SlotSet('genre',None),SlotSet('keyword',None),SlotSet('language',None),SlotSet('media',None),SlotSet('original_title',None),	SlotSet('original_language',None),SlotSet('plot',None),SlotSet('Producer',None),SlotSet('rank_axis',None),SlotSet('ranked_col',None),SlotSet('revenue',None),SlotSet('row_number',None),SlotSet('row_range',None),SlotSet('sort_col',None),SlotSet('top_bottom',None),SlotSet('year',None),SlotSet('ascending_descending',None)]

'''
        for slot in slot_dict:
            logging.warning("CAROUSEL slot is "+str(slot)+" "+str(slot_dict[slot]))
        for movie_dict in carousel_payload["movie_list"]:
            main_title_str = movie_dict["original_title"]+"("+movie_dict["year"]+")"
            main_title.append(main_title_str)
            if len(movie_dict["character"]) == 0:
                sub_title_str = "not named"
            else: 
                # str(my_list3).strip('[]')
                sub_title_str = str(movie_dict["character"]).strip('[]')
            sub_title.append(sub_title_str)
            img.append(movie_dict["poster_path"])
        
        target_URL = wv_URL
        logging.warning("CAROUSEL condition_col "+str(condition_col))
        logging.warning("CAROUSEL raw_key "+str(raw_key))
        if len(img) > 0:
            logging.warning("CAROUSEL poster URL "+str(img[0]))
            for i in range(0,2):
                logging.warning("CAROUSEL main_title "+str(main_title[i]))
                logging.warning("CAROUSEL sub_title "+str(sub_title[i]))
                logging.warning("CAROUSEL img "+str(img[i]))
            message6 =  {
                   "attachment":{
                     "type":"template",
                     "payload":{
                       "template_type":"generic",
                       "elements":[
                          {
                           "title":main_title[0],
                           "image_url":img[0],
                           "subtitle":sub_title[0],
                           "buttons":[
                          {
                           "type":"web_url",
                           "url":target_URL,
                           "title":"Movie Details",
                           "messenger_extensions": "true",
                           "webview_height_ratio": "tall"
                          }]},
                          {
                           "title":main_title[1],
                           "image_url":img[1],
                           "subtitle":sub_title[1],
                           "buttons":[
                          {
                           "type":"web_url",
                           "url":target_URL,
                           "title":"Movie Details",
                           "messenger_extensions": "true",
                           "webview_height_ratio": "tall"
                          }]}                            
                        ]      
                      }
                    }
                  }
'''
      
class action_show_details(Action):
   """special demo action to show canned web page - TODO provide a less hacky way to do this"""
   def name(self) -> Text:
      return "action_show_details"
   def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
      #
      tracker_value = tracker.get_latest_input_channel()
      logging.warning("IN ACTION SHOW DETAILS TRACKER_VALUE "+str(tracker_value))
      global wv_payload
      raw_movie = tracker.get_slot('original_title')
      logging.warning("raw_movie is "+str(raw_movie))
      slot_dict = {}
      slot_dict = tracker.current_slot_values()
      try:
         if slot_dict['original_title'] == "Ballroom Blitz":
            img = "https://www.youtube.com/watch?v=gYnRmfgKAbg"
            logging.warning("ready Mick?")
         else:
            logging.warning("not a video "+str(slot_dict['original_title']))
            # for compare ensure that lowercasing and removal of punctuation done
            poster_file = df_dict['movies'][df_dict['movies']['original_title'].apply(lambda x: prep_compare(x)) == prep_compare(slot_dict['original_title'])]['poster_path']
            if len(poster_file) == 0:
               logging.warning("trying fuzzy match for "+prep_compare(slot_dict['original_title']))
               # if no exact match try for fuzzy match
               poster_file = df_dict['movies'][(df_dict['movies']['original_title'].apply(lambda x: prep_compare(x))).str.contains(prep_compare(slot_dict['original_title']))]['poster_path']
               #poster_file = df_dict['movies'][df_dict['movies']['original_title'].str.lower()==slot_dict['original_title'].lower()]['poster_path']
            logging.warning("poster_file is "+str(poster_file.iloc[0]))
            # TODO for test need URL of this form http://127.0.0.1:5000/rhIRbceoE9lR4veEXuwCC2wARtG.jpg
            #target_URL = "https://webviewfm.ngrok.io/"
            target_URL = wv_URL
            #target_URL = "https://cbc.ca"
            logging.warning("target_URL is "+str(target_URL))
            # want to make call to build display object here
            # TODO post demo 1, generalize this to be any key_slot rather than just original_title
            wv_payload = get_wv_payload('original_title',raw_movie)
            for wv_payload_index in wv_payload:
                logging.warning("wv_payload index is "+str(wv_payload_index))
                logging.warning("display content is "+str(wv_payload[wv_payload_index].display_content))
                logging.warning("display type is "+str(wv_payload[wv_payload_index].display_type))
                logging.warning("return type is "+str(wv_payload[wv_payload_index].return_type))
                logging.warning("return payload is "+str(wv_payload[wv_payload_index].return_payload))
            # pass wv_payload to flask
            load_wv_payload(wv_payload)
            message1 = {
               "attachment": {
                    "type": "template",
                    "payload": {
                      "template_type": "button",
                      "text": "Test URL button for webview",
                      "buttons": [
                        {
                           "type":"web_url",
                           "url":target_URL,
                           "title":"URL Button",
                           "messenger_extensions": "true",
                           "webview_height_ratio": "tall"
                        }
                     ]
                  }
               }
            }
            gt = {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "generic",
                    "elements": [
                        {
                            "title": "Welcome! 1",
                            "image_url": "https://picsum.photos/200",
                            "subtitle": "We have the right hat for everyone.",
                            "default_action": {
                                "type": "web_url",
                                "url": target_URL,
                                "webview_height_ratio": "tall",
                            },
                            "buttons": [
                                {
                                    "type": "web_url",
                                    "url": target_URL,
                                    "title": "View Website"
                                },
                                {
                                    "type": "postback",
                                    "title": "Start Chatting",
                                    "payload": "DEVELOPER_DEFINED_PAYLOAD"
                                }
                            ]
                        },
                        {
                            "title": "Welcome! 2",
                            "image_url": "https://picsum.photos/200",
                            "subtitle": "We have the right hat for everyone.",
                            "default_action": {
                                "type": "web_url",
                                "url": target_URL,
                                "webview_height_ratio": "tall",
                            },
                            "buttons": [
                                {
                                    "type": "web_url",
                                    "url": target_URL,
                                    "title": "View Website"
                                },
                                {
                                    "type": "postback",
                                    "title": "Start Chatting",
                                    "payload": "DEVELOPER_DEFINED_PAYLOAD"
                                }
                            ]
                            }
                        ]
                    }
                }
            }
            dispatcher.utter_custom_json(message1)
            dispatcher.utter_message("COMMENT - past posting to FM Jan 31")
      except:
         if debug_on:
            raise
         dispatcher.utter_message("could not find media for show details - please try another query")
      logging.warning("COMMENT: end of transmission show details validated")
      #
      return[SlotSet('budget',None),SlotSet('cast_name',None),SlotSet('character',None),SlotSet('condition_col',None),SlotSet('condition_operator',None),SlotSet('condition_val',None),SlotSet('Costume_Design',None),SlotSet('Director',None),SlotSet('Editor',None),SlotSet('file_name',None),SlotSet('genre',None),SlotSet('keyword',None),SlotSet('language',None),SlotSet('media',None),SlotSet('original_title',None),	SlotSet('original_language',None),SlotSet('plot',None),SlotSet('Producer',None),SlotSet('rank_axis',None),SlotSet('ranked_col',None),SlotSet('revenue',None),SlotSet('row_number',None),SlotSet('row_range',None),SlotSet('sort_col',None),SlotSet('top_bottom',None),SlotSet('year',None),SlotSet('ascending_descending',None)]




class action_list_category(Action):
   """for a given category, show quick responses for the category labels"""
   def name(self) -> Text:
      return "action_list_category"
   def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
      logging.warning("IN ACTION LIST CATEGORY")
      global display_mode
      category = tracker.get_slot('category')
      category_table = category_table_dict[category]
      logging.warning("category is "+str(category))
      logging.warning("category_table is "+str(category_table))
      # get unique values in the name column of the category_table
      # a = df['A'].unique()
      col_name = category_table_name[category]+"_name"
      logging.warning("col_name is "+str(col_name))
      category_values = category_table[col_name].unique()
      logging.warning("category_values are "+str(category_values))
      # build list of quick responses
      # print out max_qr_per_row per row and then send to FM
      qr_count = 0
      i = 0
      qr_list = []
      for value in category_values:
         payload_text = "top "+value+" movies"
         logging.warning("payload_text is "+payload_text)
         qr_list.append({"content_type":"text",
                       "payload": payload_text,
                       "title": value})
         i = i+1
         qr_count = qr_count+1
         if i >= max_qr:
            break
      list_category_text = "Ok, "+category+". Choose one of these, or ask me about a different one."
      list_category_message = {               
                      "text": list_category_text,
                      "quick_replies": qr_list
                      }
      dispatcher.utter_custom_json(list_category_message)
      '''
         if qr_count >= max_qr_per_row:
            # output a row of QRs
            qr_count = 0
            list_category_text = "Ok, "+category+". Choose one of these, or ask me about a different one."
            list_category_message = {               
                      "text": list_category_text,
                      "quick_replies": qr_list
                      }
            dispatcher.utter_custom_json(list_category_message)
            qr_list = []
      '''
      logging.warning("list_category_message is "+str(list_category_message))
        
      # set the display mode to detailed so that the results are clickable
      logging.warning("display_mode 3 is: "+display_mode)
      display_mode = "details"
      return[SlotSet('detail_mode','details'),SlotSet('budget',None),SlotSet('cast_name',None),SlotSet('character',None),SlotSet('condition_col',None),SlotSet('condition_operator',None),SlotSet('condition_val',None),SlotSet('Costume_Design',None),SlotSet('Director',None),SlotSet('Editor',None),SlotSet('file_name',None),SlotSet('genre',None),SlotSet('keyword',None),SlotSet('language',None),SlotSet('media',None),SlotSet('original_title',None),	SlotSet('original_language',None),SlotSet('plot',None),SlotSet('Producer',None),SlotSet('rank_axis',None),SlotSet('ranked_col',None),SlotSet('revenue',None),SlotSet('row_number',None),SlotSet('row_range',None),SlotSet('sort_col',None),SlotSet('top_bottom',None),SlotSet('year',None),SlotSet('ascending_descending',None)]





class action_welcome_page(Action):
   """welcome responses after initial FM page"""
   def name(self) -> Text:
      return "action_welcome_page"
   def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
      logging.warning("IN INITIALIZE FM")
      most_recent_state = tracker.current_state()
      sender_id = most_recent_state['sender_id']
      fb_access_token = "EAAKrBDkZCQtgBAPkGlFtV4VqvcSggjDV1Sf8ClnZBmYagK4ZBQHtcZB9W5sOKBZCjRjad3ZCEZBFXo6ZACmZCzFte2xDxzHrkyKFCNEjmWuZBR72ZBxkoJiZCBFUC6ZBTgGVKLPZBE3yL7IQT86hLyEvTor4F1sb6Vg8gkBMCrQVi5QfzQuQZDZD"
      r = requests.get('https://graph.facebook.com/{}?fields=first_name,last_name,locale,timezone,gender,profile_pic&access_token={}'.format(sender_id, fb_access_token)).json()
      first_name = r['first_name']
      last_name = r['last_name']
      tz_fb = r['timezone']
      gender_fb = r['gender']
      locale_fb = r['locale']
      string_fb = "gender is "+str(gender_fb)+" timezone is "+str(tz_fb)+" locale is "+str(locale_fb)
      # dispatcher.utter_message(string_fb)
      conf_string = "Hello, "+first_name+", I'm Movie Molly! Ask me about your favourite movie or actor,"
      dispatcher.utter_message(conf_string)
      genre_payload = "show genres"
      top_rated_payload = "show top films"
      actor_payload = "show top actors"
      message4 = {
               "attachment": {
                    "type": "template",
                    "payload": {
                      "template_type": "button",
                      "text": "Test rasa payload button in FM",
                      "buttons": [
                        {
                          "type": "postback",
                          "payload": genre_payload,
                          "title": "Genre"
                        },
                        {
                          "type": "postback",
                          "payload": top_rated_payload,
                          "title": "Top Rated"
                        },
                        {
                          "type": "postback",
                          "payload": actor_payload,
                          "title": "Actors"
                        }
                      ]
                    }
                  }
                }
      message5 = {               
                      "text": "or select a category from the menu below ",
                      "quick_replies": [
                        {
                          "content_type": "text",
                          "payload": genre_payload,
                          "title": "Genre"                          
                        },
                        {
                          "content_type": "text",
                          "payload": top_rated_payload,
                          "title": "Top Rated"                          
                        },
                        {
                          "content_type": "text",
                          "payload": actor_payload,
                          "title": "Actors"
                        }
                      ]
                    }
      dispatcher.utter_custom_json(message5)
      logging.warning("after buttons")
      return [SlotSet('name', first_name), SlotSet('surname', last_name)]

# persistent menu not working yet
'''
      message_fm =   {
            "persistent_menu": [
            {
               "locale": "default",
               "composer_input_disabled": False,
               "call_to_actions": [
               {
                    "type": "postback",
                    "title": "Genre",
                    "payload": "list genres"
                },
                {
                    "type": "postback",
                    "title": "Top Rated",
                    "payload": "list top rated"
                },
                {
                    "type": "postback",
                    "title": "Actors",
                    "payload": "list actors"
                }
               ]
              }
          ]
      }
      
      dispatcher.utter_custom_json(message_fm)
'''
  


   

class action_condition_by_media(Action):
   """return the values from movie table"""
   def name(self) -> Text:
      return "action_condition_by_media"
   def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
      logging.warning("IN CONDITION BY MEDIA")
      raw_movie = tracker.get_slot('original_title')
      logging.warning("raw_movie is "+str(raw_movie))
      slot_dict = {}
      slot_dict = tracker.current_slot_values()
      # TODO generalize this code to deal with media in general - some kind of metadata in schema to identify media-related columns
      # and code to find media file names and paths and render per media type
      # load the media type
      media_type = media_dict[slot_dict["media"]]
      logging.warning("slot_dict['original_title'] is "+str(slot_dict['original_title']))
      logging.warning("target is "+prep_compare(slot_dict['original_title']))
      try:
         if slot_dict['original_title'] == "Ballroom Blitz":
            img = "https://www.youtube.com/watch?v=gYnRmfgKAbg"
            logging.warning("ready Mick?")
         else:
            logging.warning("not a video "+str(slot_dict['original_title']))
            # for compare ensure that lowercasing and removal of punctuation done
            poster_file = df_dict['movies'][df_dict['movies']['original_title'].apply(lambda x: prep_compare(x)) == prep_compare(slot_dict['original_title'])]['poster_path']
            if len(poster_file) == 0:
               logging.warning("trying fuzzy match for "+prep_compare(slot_dict['original_title']))
               # if no exact match try for fuzzy match
               poster_file = df_dict['movies'][(df_dict['movies']['original_title'].apply(lambda x: prep_compare(x))).str.contains(prep_compare(slot_dict['original_title']))]['poster_path']
               #poster_file = df_dict['movies'][df_dict['movies']['original_title'].str.lower()==slot_dict['original_title'].lower()]['poster_path']
            logging.warning("poster_file is "+str(poster_file.iloc[0]))
            img = image_path+str(poster_file.iloc[0])
            img_small = image_path_dict["small"]+str(poster_file.iloc[0])
            img_medium = image_path_dict["medium"]+str(poster_file.iloc[0])
         logging.warning("img is "+str(img))
         logging.warning("latest_input_channel "+str(tracker.get_latest_input_channel()))
         logging.warning("media_type is "+str(media_type))
         mess4_payload_plot = "plot for "+str(slot_dict['original_title'])
         mess4_payload_stars = "stars of "+str(slot_dict['original_title'])
         mess4_payload_director = "director of "+str(slot_dict['original_title'])
         mess4_payload_rating = "rating for "+str(slot_dict['original_title'])
         mess4_payload_stars = "actors in "+str(slot_dict['original_title'])
         mess4_payload_genre = "genre of "+str(slot_dict['original_title'])
         # special incantation required to get a graphic to display - none of the 3 other half-baked recommendations worked
         if tracker.get_latest_input_channel() == 'facebook':
            message = {
               "attachment": {
                  "type": media_type,
                  "payload": {
                     "url": img
                  }
               }
            }
            
            logging.warning("about to utter_custom_json for "+str(tracker.get_latest_input_channel()))
            dispatcher.utter_custom_json(message)
            fb_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
            '''
            message2 = {
                "attachment":{
                  "type":"template",
                  "payload":{
                    "template_type":"generic",
                    "elements":[
                       {
                        "title":"Critical details for Karma AI leadership team eyes only",
                         "default_action": {
                         "type": "web_url",
                          "url": fb_url,
                          "messenger_extensions": True,
                          "fallback_url": fb_url
                        },
                        "buttons":[
                          {
                            "type":"web_url",
                            "title": "open link",
                            "url":fb_url
                          }              
                        ]      
                      }
                    ]
                  }
             }
            }'''

            message3 = {
                  "attachment": {
                    "type": "template",
                    "payload": {
                      "template_type": "button",
                      "text": "Test link from button in FM",
                      "buttons": [
                        {
                          "type": "web_url",
                          "url": fb_url,
                          "title": "Click here"
                        }
                      ]
                    }
                  }
                }
            # test payload standard buttons
            message4 = {
               "attachment": {
                    "type": "template",
                    "payload": {
                      "template_type": "button",
                      "text": "Test rasa payload button in FM",
                      "buttons": [
                        {
                          "type": "postback",
                          "payload": mess4_payload_plot,
                          "title": "click to get plot"
                        },
                        {
                          "type": "postback",
                          "payload": mess4_payload_stars,
                          "title": "click to get stars"
                        },
                        {
                          "type": "postback",
                          "payload": mess4_payload_director,
                          "title": "click to get director"
                        }
                      ]
                    }
                  }
                }
            # test side by side buttons
            message5 = {
               
                      "text": "What do you want next?",
                      "quick_replies": [
                        {
                          "content_type": "text",
                          "payload": mess4_payload_plot,
                          "title": " ",
                          "image_url":"https://github.com/ryanmark1867/chatbot/raw/master/images/thumb_up.jpg"
                        },
                        {
                          "content_type": "text",
                          "payload": mess4_payload_stars,
                          "title": " ",
                          "image_url":"https://github.com/ryanmark1867/chatbot/raw/master/images/thumb_down.jpg"
                        },
                        {
                          "content_type": "text",
                          "payload": mess4_payload_director,
                          "title": "click to get *director*"
                        },
                        {
                          "content_type": "text",
                          "payload": mess4_payload_plot,
                          "title": "click to get *plot2*"
                        },
                        {
                          "content_type": "text",
                          "payload": mess4_payload_stars,
                          "title": "click to get stars2"
                        },
                        {
                          "content_type": "text",
                          "payload": mess4_payload_director,
                          "title": "click to get director2"
                        },
                        {
                           "content_type": "text",
                          "payload": mess4_payload_plot,
                          "title": "click to get plot3"
                        },
                        {
                          "content_type": "text",
                          "payload": mess4_payload_stars,
                          "title": "click to get stars3"
                        },
                        {
                          "content_type": "text",
                          "payload": mess4_payload_director,
                          "title": "click to get director3"
                        },
                        {
                           "content_type": "text",
                          "payload": mess4_payload_plot,
                          "title": "click to get plot4"
                        },
                        {
                          "content_type": "text",
                          "payload": mess4_payload_stars,
                          "title": "click to get stars4"
                        },
                        {
                          "content_type": "text",
                          "payload": mess4_payload_director,
                          "title": "click to get director4"
                        },
                        {
                          "content_type": "text",
                          "payload": mess4_payload_rating,
                          "title": "click to get rating"
                        }
                      ]
                    }
               
            
            message6 =  {
                   "attachment":{
                     "type":"template",
                     "payload":{
                       "template_type":"generic",
                       "elements":[
                          {
                           "title":str(slot_dict['original_title']),
                           "image_url":img,
                           "subtitle":"Click below for more details",
                           "buttons":[
                          {
                              "type": "postback",
                              "payload": mess4_payload_director,
                              "title": "Director"                            
                           },
                          {
                              "type": "postback",
                              "payload": mess4_payload_stars,
                              "title": "Stars"                            
                           },{
                              "type": "postback",
                              "payload": mess4_payload_genre,
                              "title": "Genre"
                           }]},
                          {
                           "title":str(slot_dict['original_title']),
                           "image_url":img,
                           "subtitle":"Click below for more details2",
                           "buttons":[
                          {
                              "type": "postback",
                              "payload": mess4_payload_director,
                              "title": "Director2"                            
                           },
                          {
                              "type": "postback",
                              "payload": mess4_payload_stars,
                              "title": "Stars2"                            
                           },{
                              "type": "postback",
                              "payload": mess4_payload_genre,
                              "title": "Genre2"
                           }
                            
                        ]      
                      }
                    ]
                  }
                }
              }        
            dispatcher.utter_custom_json(message5)
         else:
            dispatcher.utter_message(img)
      except:
         if debug_on:
            raise
         dispatcher.utter_message("could not find media - please try another query")
      logging.warning("COMMENT: end of transmission validated")
      #return [SlotSet("ranked_col",None),SlotSet("character",None),SlotSet("movie",None),SlotSet("media",None),SlotSet("rank_axis",None),SlotSet("keyword",None),SlotSet("year",None),SlotSet("genre",None),SlotSet("plot",None),SlotSet("Director",None),SlotSet("cast_name",None)]
      return[SlotSet('budget',None),SlotSet('cast_name',None),SlotSet('character',None),SlotSet('condition_col',None),SlotSet('condition_operator',None),SlotSet('condition_val',None),SlotSet('Costume_Design',None),SlotSet('Director',None),SlotSet('Editor',None),SlotSet('file_name',None),SlotSet('genre',None),SlotSet('keyword',None),SlotSet('language',None),SlotSet('media',None),SlotSet('original_title',None),	SlotSet('original_language',None),SlotSet('plot',None),SlotSet('Producer',None),SlotSet('rank_axis',None),SlotSet('ranked_col',None),SlotSet('revenue',None),SlotSet('row_number',None),SlotSet('row_range',None),SlotSet('sort_col',None),SlotSet('top_bottom',None),SlotSet('year',None),SlotSet('ascending_descending',None)]


# set FM welcome screen text
'''
class action_welcome_page(Action):
   """invoke FM welcome page"""
   def name(self) -> Text:
      return "action_welcome_page"
   def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
      logging.warning("COMMENT: got a welcome_page")
      dispatcher.utter_message("Hello <<Name>> I'm Movie Molly. I know a lot about movies. Ask me something")
      return[]
'''






class action_condition_by_language(Action):
   """return the values scoped by year"""
   def name(self) -> Text:
      return "action_condition_by_language"
   def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
      slot_dict = {}
      slot_dict = tracker.current_slot_values()
      #for slot_entry in slot_dict:
      #   dispatcher.utter_message(str(slot_entry))
      #   dispatcher.utter_message(str(slot_dict[slot_entry]))
      ranked_col = tracker.get_slot("ranked_col")
      language = tracker.get_slot("language")
      top_bottom = tracker.get_slot("top_bottom")
      if top_bottom == 'top':
         ascend_direction = False
      else:
         ascend_direction = True
      csv_row = int(tracker.get_slot('row_number'))
      sort_col = tracker.get_slot("sort_col")
      str1 = "COMMENT: "+ str(path_dict['movies'])
      dispatcher.utter_message(str1)
      df=df_dict['movies']
      ranked_col = slot_map[ranked_col]
      language = slot_map[language]
      result = df[df['original_language'] == language][ranked_col]
      dispatcher.utter_message(str(result))
      dispatcher.utter_message("COMMENT: end of transmission")
      return []

# Property of KarmaAI 