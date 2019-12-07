import pandas as pd
import glob
import os
import json


def load_all_csv(pattern):
    """
    Load all json files that match in the given glob pattern.
    
    Arg:
        pattern(str): Pattern for glob to match files.
    """
    assert isinstance(pattern, str)
    
    # Import all the CSV files that matches given `pattern`
    files = [i for i in glob.glob(pattern)]
    sorted(files)
    print(files)

    # Combine all the statistics from different regions
    dfs = list()
    for file in files:
        df = pd.read_csv(file, index_col='video_id', encoding='latin1')
        # Extract first two characters from file name and use it as code for country
        df['country'] = os.path.basename(file)[:2]
        dfs.append(df)

    df = pd.concat(dfs)
    
    return df


def cleanup_df(df):
    """
    Pipeline for cleaning up the dataframe.

    Arg:
        df(pandas.DataFrame): Dataframe to be processed.a
    """
    # Fill nan with some default values
    df["description"] = df["description"].fillna(value="")
    
    # Reformat values
    reformat_time(df, "trending_date", "%y.%d.%m")
    reformat_time(df, "publish_time", "%Y-%m-%dT%H:%M:%S.%fZ")

    df = df.dropna(how='any',inplace=False, axis=0)


def reformat_time(df, col, template):
    """
    Reformat the date time and removed the incompleted rows
    
    Args:
        df(pandas.DataFrame): Dataframe to be processed.
        col(str): Column to be reformatted.
        template(str): Time string template for the given column.
    """
    assert isinstance(col, str)
    assert isinstance(template, str)
    
    df[col] = pd.to_datetime(df[col], errors='coerce', format=template)
    df = df[df[col].notnull()]


def fill_category(df, src="./data/category_id/US_category_id.json"):
    """
    Insert category ID to the given input pd.DataFrame `df` according
    to the path `src`. Insertion is performed inplace.
    
    Args:
        df(pandas.DataFrame): Dataframe to be processed.
        src(src): Path to category mapping file.
    """
    assert isinstance(src, str) and os.path.exists(src)
    
    # Cast the dtype to `str`
    df['category_id'] = df["category_id"].astype(str)

    category_id = {}
    with open(src, "r") as f:
        data = json.load(f)
        for category in data['items']:
            category_id[category['id']] = category['snippet']['title']

    df.insert(4, 'category', df['category_id'].map(category_id))
    # category_list = df['category'].unique()