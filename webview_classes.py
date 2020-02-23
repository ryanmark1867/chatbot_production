# classes defined to share information with the code responsible for generating the dynamic web content

class movie_info:
    '''define the characteristics that need to be carried for movies'''
    def __init__(self,poster_url, original_title, year, rating,run_time,genre_list,director_list,actor_list,crew_dict,overview):
        self.poster_url = poster_url
        self.original_title = original_title
        self.year = year
        self.rating = rating
        self.run_time = run_time
        self.genre_list = genre_list
        self.director_list = director_list
        self.actor_list = actor_list
        self.crew_dict = crew_dict
        self.overview = overview
        
class condition_class:
    ''' the set of metadata required to get the value for a particular element of a movie_info instance '''
    def __init__(df,cond_col, val_col):
        self.df = df # the dataframe that contains the value
        self.cond_col = cond_col # the column in the dataframe that contains the condition (e.g. parent_key)
        self.val_col = val_col # the column in the dataframe that contains the value
        self.rating = rating
        self.run_time = run_time
        self.genre_list = genre_list
        self.director_list = director_list
        self.actor_list = actor_list
        self.crew_dict = crew_dict
        self.plot = plot   

class payload_item:
    ''' object that makes up payload dictionary sent to dynamic web server to display details'''
    def __init__(self,display_content,display_type,return_type, return_payload):
        self.display_content = display_content # what gets shown in webview
        self.display_type = display_type # how it gets shown: text, link, image
        self.return_type = return_type # where action occurs if this item is selected: fm (close wv and return payload back to Facebook Messenger), wv (stay in wv and take action there)
        self.return_payload = return_payload # what gets sent back if this display item gets selected
        
class carousel_tracker:
    ''' object that maintains persistent information about carousel '''
    def __init__(self,before_movie_index,after_movie_index,carousel_size, carousel_dict):
        self.before_movie_index = before_movie_index
        self.after_movie_index = after_movie_index
        self.carousel_size = carousel_size
        self.carousel_dict = carousel_dict