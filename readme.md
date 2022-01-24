# EasyTravel_telegram_bot



An application that searches for hotels by several criteria.
The application can be used as an alternative to a website for a small travel company.The bot can be used by an employee of the company and as a tool for automatic selection according to specified parameters, by the company's clients.


## Commands

- /city (implemented as the main command, the user enters the city and decides which sorting method to choose)
- /lowprice (Finds the cheapest hotels in a given city. It gives the result if one adult is accommodated with the price for one night)
- /highprice (Finds the most expensive hotels in a given city. It gives the result if one adult is accommodated with the price for one night)
- /bestdeal (Selects a hotel in a given city based on the range of prices and distances from the city center specified by the user)



### city command
The city team implements the algorithm of work through a request from the user 
for the name of the city, and then offers to choose a method 
for choosing a hotel using the methods described below, 
this command is implemented automatically: 
the bot automatically accepts the name of the city for input.


### lowprice command
The command is called by entering /lowprice 
and implements the search for cheap hotels.
 First, the city is requested, then the number of hotels.

### highprice command
The command is called by entering /highprice
and implements the search for expensive hotels. 
First, the city is requested, then the number of hotels

### bestdeal command
The command is called by entering /bestdeal
and implements the search for hotels by the specified parameters.
The user is asked for the minimum and maximum values of the hotel prices
and the range of distances from the city center


The basic logic of the bot is reduced to the fact that the user 
does not need to enter commands, just enter the name of the city, 
then the bot itself will suggest which method to search for hotels.

```
def get_text_messages(message: telebot.types.Message) -> None:

	user = User.get_user(message.from_user.id)
	if message.text in ['/lowprice', '/highprice']:
		method_sort(message, user)
	elif message.text == "/bestdeal":
		bestdeal_city(message, user)
	elif message.text == "/city":
		get_name_city(message, user)
	else:
		get_answer_city(message, user)
```


## Installation

Installing the bot is very simple. 
You need to clone the contents of the repository or download a zip archive.
Since the project uses pipenv, you need to add the .env file to the downloaded
project. In the new file, you must specify the bot's telegram token 
and the token rapidapi.

Then you need to place the project on a hosting service.

On the hosting, we install Pipenv in our project via the console 
and clone all the project dependencies.
````
pip install pipenv
````
````
pipenv sync
````
