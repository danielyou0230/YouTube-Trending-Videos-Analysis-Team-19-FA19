
## Overview:

	The directory is composed of a data folder, a scraper folder ,several .py files, a main.ipynb and a README.md. The data folder contains the data from Kaggle Dataset "Trending YouTube Video Statistics"(https://www.kaggle.com/datasnaek/youtube-new/metadata) and the data scrapped by Google's YouTube Trending Videos API. The scraper file contains all the python scripts for data scraping. The main.ipynb provides all the visualizations. The README.md provides step by step instruction on how to conduct the whole YouTube data analysis process.

## Steps:

### a. Data Scraping

The data scraping is devloped based on the Google's YouTube Trending Videos API. To run the scraper, you will need to request for a valid API key for the YouTube Data API. It is free and the instruction for getting the API key is [here](https://developers.google.com/youtube/registering_an_application). Once you have the key, paste it inside the text file  src/scraper/api_key.txt.

	-> location: scraper/Youtubescraper.py
	-> run command: python /scraper/Youtubescraper.py
	-> description: The YouTube data scrapper is implemented through the function youtubescraper(key_path='api_key.txt',country_code_path='country_codes.txt'). 
	You can modify the argument as your local position of the key_path 
	and country_code_path.
	-> data generated: data generated is stored in data/current/

If you want to use the scraper to scrap the YouTube data in more countries, you can add the corresponding 2-letter country abbreviations according to ISO 3166-1 in  src/scraper/country_codes.txt. A list of all existing ones can be found [here](https://en.wikipedia.org/wiki/ISO_3166-1#Current_codes)

For more information regarding the Google YouTube API, refer to [here](https://www.youtube.com/feed/trending).


### b. Data Preprocessing

The data preprocessing file loads the dataset contained in the csv file and preprocess the data. It removes the NULL data, reformat the time and fill out the category columns to benefit the further analysis.

```
-> location: preprocessing.py
```

### c. Data Visualizing

The data visualizing file visulizes all the results in the YouTube analysis. 

1. Rankings of contents category in each country
2. Correlation between dataset columns
3. Average days on trending list, by category’ ID
4. Publishing day and trending no. of videos
5. Category ID vs. likes/dislikes

## Jupter Notebook

The jupter notebook main.ipynb integreates all the functions in data preprocessing and data visualizing parts together. And it contains all the figures that we ultilize in our final presentation and the figures that help us to come to the final conclusion. 

```
-> Can re-run the code 
```

