import requests, sys, time, os, argparse

# List of simple to collect features
snippet_features = ["title",
                    "publishedAt",
                    "channelId",
                    "channelTitle",
                    "categoryId"]

# Any characters to exclude, generally these are things that become problematic in CSV files
unsafe_characters = ['\n', '"']

# Used to identify columns, currently hardcoded order
header = ["video_id"] + snippet_features + ["trending_date", "tags", "view_count", "likes", "dislikes",
                                            "comment_count", "thumbnail_link", "comments_disabled",
                                            "ratings_disabled", "description"]

def prepare_feature(feature):
    """
    :param feature: string of original feature scrappped
    :return: string of features where any character from the unsafe characters list is removed and surrounds the whole item in quotes
    """
    for ch in unsafe_characters:
        feature = str(feature).replace(ch, "")
    return f'"{feature}"'

def api_request(page_token, country_code):
    """
    :param page_token:
    :param country_code: 2-letter country code
    :return: JSON format of data
    """
    # Builds the URL and requests the JSON from it
    request_url = f'https://www.googleapis.com/youtube/v3/videos?part=id,statistics,snippet{page_token}chart=mostPopular&regionCode={country_code}&maxResults=50&key={api_key}'
    request = requests.get(request_url)
    #handle failure
    if request.status_code == 429:
        print("Temp-Banned due to excess requests, please wait and continue later")
        sys.exit()
    return request.json()

def get_videos(items):
    """
    :param items: JSON format of data on movie items
    :return: list of data on items
    """
    lines = []
    for video in items:
        comments_disabled = False
        ratings_disabled = False

        # We can assume something is wrong with the video if it has no statistics, often this means it has been deleted
        # so we can just skip it
        if "statistics" not in video:
            continue

        # A full explanation of all of these features can be found on the GitHub page for this project
        video_id = prepare_feature(video['id'])

        # Snippet and statistics are sub-dicts of video, containing the most useful info
        snippet = video['snippet']
        statistics = video['statistics']

        # This list contains all of the features in snippet that are 1 deep and require no special processing
        features = [prepare_feature(snippet.get(feature, "")) for feature in snippet_features]

        # The following are special case features which require unique processing, or are not within the snippet dict
        description = snippet.get("description", "")
        thumbnail_link = snippet.get("thumbnails", dict()).get("default", dict()).get("url", "")
        trending_date = time.strftime("%y.%d.%m")
        #tags = get_tags(snippet.get("tags", ["[none]"]))
        tags = prepare_feature("|".join(snippet.get("tags", ["[none]"])))
        view_count = statistics.get("viewCount", 0)

        # This may be unclear, essentially the way the API works is that if a video has comments or ratings disabled
        # then it has no feature for it, thus if they don't exist in the statistics dict we know they are disabled
        if 'likeCount' in statistics and 'dislikeCount' in statistics:
            likes = statistics['likeCount']
            dislikes = statistics['dislikeCount']
        else:
            ratings_disabled = True
            likes = 0
            dislikes = 0

        if 'commentCount' in statistics:
            comment_count = statistics['commentCount']
        else:
            comments_disabled = True
            comment_count = 0

        # Compiles all of the various bits of info into one consistently formatted line
        line = [video_id] + features + [prepare_feature(x) for x in [trending_date, tags, view_count, likes, dislikes,
                                                                       comment_count, thumbnail_link, comments_disabled,
                                                                       ratings_disabled, description]]
        lines.append(",".join(line))
    return lines


def get_pages(country_code, next_page_token="&"):
    """
    :param country_code: 2-letter country code
    :param next_page_token: whether a page has a next page,by default "&"
    :return: a list of data for the country in country_code
    """
    assert isinstance(country_code,str)
    assert len(country_code)==2
    country_data = []

    # Because the API uses page tokens (which are literally just the same function of numbers everywhere) it is much
    # more inconvenient to iterate over pages, but that is what is done here.
    while next_page_token is not None:
        # A page of data i.e. a list of videos and all needed data
        video_data_page = api_request(next_page_token, country_code)

        # Get the next page token and build a string which can be injected into the request with it, unless it's None,
        # then let the whole thing be None so that the loop ends after this cycle
        next_page_token = video_data_page.get("nextPageToken", None)
        next_page_token = f"&pageToken={next_page_token}&" if next_page_token is not None else next_page_token

        # Get all of the items as a list and let get_videos return the needed features
        items = video_data_page.get('items', [])
        country_data += get_videos(items)
    return country_data

def youtubescraper(key_path='api_key.txt',country_code_path='country_codes.txt'):
    """
    :param api_key: the filename of the txt file that contains the API key(default = api_key.txt)
    :param country_code: the filename of the txt file that contains the API key(default = country_codes.txt)
    :return: the csv files that contains the scrapped data
    """
    assert isinstance(key_path, str)
    assert isinstance(country_code_path, str)
    global api_key
    global country_codes
    output_dir = '../../data/current/'

    #Read the api_key and country codes to scrap data of
    with open(key_path, 'r') as file:
        api_key = file.readline().strip()
    file.close()
    with open(country_code_path,'r') as file:
        country_codes = [x.rstrip() for x in file]
    file.close()

    #write the extracted data in the csv file
    for country_code in country_codes:
        country_data = [",".join(header)] + get_pages(country_code)
        with open(f"{output_dir}/{country_code}videos.csv", "w+", encoding='utf-8') as file:
            for row in country_data:
                file.write(f"{row}\n")
        file.close()

youtubescraper()