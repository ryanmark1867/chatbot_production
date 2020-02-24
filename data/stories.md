## happy path
* greet
  - action_welcome_page

## New Story
* list_category{"category":"genre"}
    - slot{"category":"genre"}
    - action_list_category
	
## New Story
* show_carousel{"cast_name":"Harrison Ford"}
	- slot{"cast_name":"Harrison Ford"}
	- action_show_carousel

## New Story
* scroll_carousel{"cast_name":"Harrison Ford"}
	- slot{"cast_name":"Harrison Ford"}
	- action_scroll_carousel


## New Story
* show_details{"movie":"Blade Runner"}
	- slot{"movie":"Blade Runner"}
	- action_show_details

## New Story
* condition_by_movie{"ranked_col":"movies","cast_name":"Jack Lemmon"}
    - slot{"ranked_col":"movies"}
    - slot{"cast_name":"Jack Lemmon"}
    - action_condition_by_movie


## New Story
* condition_by_media{"media":"poster","movie":"Harry Meet Sally"}
    - slot{"media":"poster"}
    - slot{"movie":"Harry Meet Sally"}
    - action_condition_by_media

## New Story
* condition_by_media{"media":"poster","movie":"Margaret's Museum"}
    - slot{"media":"poster"}
    - slot{"movie":"Margaret's Museum"}
    - action_condition_by_media



## New Story
* condition_by_movie_ordered{"ranked_col":"movies","Director":"Woody Allen","rank_axis":"popularity"}
    - slot{"ranked_col":"movies"}
    - slot{"Director":"Woody Allen"}
	- slot{"rank_axis":"popularity"}
    - action_condition_by_movie_ordered

## New Story
* condition_by_movie_ordered{"ranked_col":"movies","row_range":"99","genre":"Thriller"}
    - slot{"ranked_col":"movies"}
    - slot{"row_range":"99"}
	- slot{"genre":"Thriller"}
    - action_condition_by_movie_ordered

## New Story
* condition_by_movie_ordered{"ranked_col":"movies","row_range":"99","genre":"Science Fiction"}
    - slot{"ranked_col":"movies"}
    - slot{"row_range":"99"}
	- slot{"genre":"Science Fiction"}
    - action_condition_by_movie_ordered

## New Story
* condition_by_movie_ordered{"ranked_col":"movies","year":"1996","rank_axis":"popularity"}
    - slot{"ranked_col":"movies"}
    - slot{"year":"1996"}
	- slot{"rank_axis":"popularity"}
    - action_condition_by_movie_ordered

## New Story
* condition_by_movie_ordered{"ranked_col":"movies","year":"1996"}
    - slot{"ranked_col":"movies"}
    - slot{"year":"1996"}
    - action_condition_by_movie_ordered
	



## New Story
* condition_by_movie{"ranked_col":"movies","Director":"Woody Allen"}
    - slot{"ranked_col":"movies"}
    - slot{"Director":"Woody Allen"}
    - action_condition_by_movie

# New Story
* condition_by_movie{"ranked_col":"characters","cast_name":"Tom Hanks"}
    - slot{"ranked_col":"characters"}
    - slot{"cast_name":"Tom Hanks"}
    - action_condition_by_movie

# New Story
* condition_by_movie{"ranked_col":"characters","ranked_col":"movies","cast_name":"Meryl Streep"}
    - slot{"ranked_col":"characters"}
	- slot{"ranked_col":"movies"}
    - slot{"cast_name":"Meryl Streep"}
    - action_condition_by_movie

## New Story
* condition_by_movie{"ranked_col":"cast_name","movie":"The Ten Commandments"}
    - slot{"movie":"The Ten Commandments"}
    - slot{"ranked_col":"cast_name"}
    - action_condition_by_movie
	
## New Story
* condition_by_movie{"ranked_col":"plot","movie":"Taxi Driver"}
    - slot{"movie":"Taxi Driver"}
    - slot{"ranked_col":"plot"}
    - action_condition_by_movie

## New Story
* condition_by_movie{"ranked_col":"plot","movie":"Toy Story"}
    - slot{"movie":"Toy Story"}
    - slot{"ranked_col":"plot"}
    - action_condition_by_movie

## New Story
* condition_by_movie{"genre":"Comedy","keyword":"vampire","ranked_col":"movie"}
    - slot{"genre":"Comedy"}
    - slot{"keyword":"vampire"}
	- slot{"ranked_col":"movie"}
    - action_condition_by_movie

## New Story
* condition_by_movie{"movie":"Three Easy Pieces","ranked_col":"year"}
    - slot{"movie":"Three Easy Pieces"}
    - slot{"ranked_col":"year"}
    - action_condition_by_movie

## New Story
* condition_by_movie{"ranked_col":"plot","movie":"The Exorcist"}
    - slot{"movie":"The Exorcist"}
    - slot{"ranked_col":"plot"}
    - action_condition_by_movie
	
## New Story
* condition_by_movie{"ranked_col":"budget","movie":"Goldfinger"}
    - slot{"movie":"Goldfinger"}
    - slot{"ranked_col":"budget"}
    - action_condition_by_movie

## New Story
* condition_by_movie{"ranked_col":"rating","movie":"Captain America"}
    - slot{"ranked_col":"rating"}
    - slot{"movie":"Captain America"}
    - action_condition_by_movie	

## New Story
* condition_by_movie{"ranked_col":"movies","keyword":"midlife crisis"}
    - slot{"ranked_col":"movies"}
    - slot{"keyword":"midlife crisis"}
    - action_condition_by_movie
	
	

