## happy path
* greet
  - action_welcome_page
  
## goodbye
* goodbye
  - action_goodbye

## thumbs_down
* thumbs_down
  - action_thumbs_down


## New Story
* list_category{"category":"genre"}
    - slot{"category":"genre"}
    - action_list_category
	
## New Story
* show_carousel{"cast_name":"Harrison Ford"}
	- slot{"cast_name":"Harrison Ford"}
	- action_show_carousel

## New Story
* show_genre_carousel{"genre":"Science Fiction"}
	- slot{"genre":"Science Fiction"}
	- action_show_genre_carousel

## New Story
* scroll_carousel{"cast_name":"Harrison Ford","scroll_start":"0","scroll_end":"1"}
	- slot{"cast_name":"Harrison Ford"}
	- slot{"scroll_start":"0"}
	- slot{"scroll_end":"1"}
	- action_scroll_carousel

## New Story
* show_details{"original_title":"Blade Runner"}
	- slot{"original_title":"Blade Runner"}
	- action_show_details

## New Story
* condition_by_movie{"ranked_col":"original_title","cast_name":"Jack Lemmon"}
    - slot{"ranked_col":"original_title"}
    - slot{"cast_name":"Jack Lemmon"}
    - action_condition_by_movie


## New Story
* condition_by_media{"media":"poster","original_title":"Harry Meet Sally"}
    - slot{"media":"poster"}
    - slot{"original_title":"Harry Meet Sally"}
    - action_condition_by_media

## New Story
* condition_by_media{"media":"poster","original_title":"Margaret's Museum"}
    - slot{"media":"poster"}
    - slot{"original_title":"Margaret's Museum"}
    - action_condition_by_media



## New Story
* condition_by_movie_ordered{"ranked_col":"original_title","Director":"Woody Allen","rank_axis":"popularity"}
    - slot{"ranked_col":"original_title"}
    - slot{"Director":"Woody Allen"}
	- slot{"rank_axis":"popularity"}
    - action_condition_by_movie_ordered

## New Story
* condition_by_movie_ordered{"ranked_col":"original_title","row_range":"99","genre":"Thriller"}
    - slot{"ranked_col":"original_title"}
    - slot{"row_range":"99"}
	- slot{"genre":"Thriller"}
    - action_condition_by_movie_ordered

## New Story
* condition_by_movie_ordered{"ranked_col":"original_title","row_range":"99","genre":"Science Fiction"}
    - slot{"ranked_col":"original_title"}
    - slot{"row_range":"99"}
	- slot{"genre":"Science Fiction"}
    - action_condition_by_movie_ordered

## New Story
* condition_by_movie_ordered{"ranked_col":"original_title","year":"1996","rank_axis":"popularity"}
    - slot{"ranked_col":"original_title"}
    - slot{"year":"1996"}
	- slot{"rank_axis":"popularity"}
    - action_condition_by_movie_ordered

## New Story
* condition_by_movie_ordered{"ranked_col":"original_title","year":"1996"}
    - slot{"ranked_col":"original_title"}
    - slot{"year":"1996"}
    - action_condition_by_movie_ordered
	



## New Story
* condition_by_movie{"ranked_col":"original_title","Director":"Woody Allen"}
    - slot{"ranked_col":"original_title"}
    - slot{"Director":"Woody Allen"}
    - action_condition_by_movie

# New Story
* condition_by_movie{"ranked_col":"characters","cast_name":"Tom Hanks"}
    - slot{"ranked_col":"characters"}
    - slot{"cast_name":"Tom Hanks"}
    - action_condition_by_movie

# New Story
* condition_by_movie{"ranked_col":"characters","ranked_col":"original_title","cast_name":"Meryl Streep"}
    - slot{"ranked_col":"characters"}
	- slot{"ranked_col":"original_title"}
    - slot{"cast_name":"Meryl Streep"}
    - action_condition_by_movie

## New Story
* condition_by_movie{"ranked_col":"cast_name","original_title":"The Ten Commandments"}
    - slot{"original_title":"The Ten Commandments"}
    - slot{"ranked_col":"cast_name"}
    - action_condition_by_movie
	
## New Story
* condition_by_movie{"ranked_col":"plot","original_title":"Taxi Driver"}
    - slot{"original_title":"Taxi Driver"}
    - slot{"ranked_col":"plot"}
    - action_condition_by_movie

## New Story
* condition_by_movie{"ranked_col":"plot","original_title":"Toy Story"}
    - slot{"original_title":"Toy Story"}
    - slot{"ranked_col":"plot"}
    - action_condition_by_movie

## New Story
* condition_by_movie{"genre":"Comedy","keyword":"vampire","ranked_col":"original_title"}
    - slot{"genre":"Comedy"}
    - slot{"keyword":"vampire"}
	- slot{"ranked_col":"original_title"}
    - action_condition_by_movie

## New Story
* condition_by_movie{"original_title":"Three Easy Pieces","ranked_col":"year"}
    - slot{"original_title":"Three Easy Pieces"}
    - slot{"ranked_col":"year"}
    - action_condition_by_movie

## New Story
* condition_by_movie{"ranked_col":"plot","original_title":"The Exorcist"}
    - slot{"original_title":"The Exorcist"}
    - slot{"ranked_col":"plot"}
    - action_condition_by_movie
	
## New Story
* condition_by_movie{"ranked_col":"budget","original_title":"Goldfinger"}
    - slot{"original_title":"Goldfinger"}
    - slot{"ranked_col":"budget"}
    - action_condition_by_movie

## New Story
* condition_by_movie{"ranked_col":"rating","original_title":"Captain America"}
    - slot{"ranked_col":"rating"}
    - slot{"original_title":"Captain America"}
    - action_condition_by_movie	

## New Story
* condition_by_movie{"ranked_col":"original_title","keyword":"midlife crisis"}
    - slot{"ranked_col":"original_title"}
    - slot{"keyword":"midlife crisis"}
    - action_condition_by_movie
	
	

