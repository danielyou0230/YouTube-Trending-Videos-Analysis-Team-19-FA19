import datetime
import json
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import wordcloud
import os


def plot_correlation(df, country, brief=[], xrot=0, yrot=0):
    """
    Plot the Pearson Correlation matrix for features in the given
    pandas.DataFrame `df`.
    
    Args:
        df(pandas.DataFrame): Dataframe to be processed.
        country(str): Country to plot the statistics, default: showing
            statistics of all countries.
        brief(list[str]): Brief version of the correlation matrix, this
            list should contain only subset of columns in `df`.
        xrot(int): Rotation for xlabel.
        yrot(int): Rotation for ylabel.
    """
    assert isinstance(df, pd.DataFrame)
    assert isinstance(country, str)
    assert isinstance(brief, list)
    assert isinstance(xrot, int) and isinstance(yrot, int)

    subset = df[df["country"] == country]
    # subset.corr()

    labels = [
        x.replace('_', ' ').title() for x in list(
            subset.select_dtypes(include=['number', 'bool']).columns.values)
    ]

    fig, ax = plt.subplots(figsize=(10, 6))
    if brief:
        sns.heatmap(subset[brief].corr(),
                    annot=True,
                    cmap=sns.cubehelix_palette(as_cmap=True),
                    ax=ax)
    else:
        sns.heatmap(subset.corr(),
                    annot=True,
                    xticklabels=labels,
                    yticklabels=labels,
                    cmap=sns.cubehelix_palette(as_cmap=True),
                    ax=ax)

    postfix = "_brief" if brief else ""
    title = "{}_corr_heatmap{}".format(country, postfix)

    # Make the figure more readable
    plt.xticks(rotation=xrot)
    plt.yticks(rotation=yrot)
    b, t = plt.ylim()
    b += 0.5
    t -= 0.5
    plt.ylim(b, t)

    plt.title(title)
    plt.tight_layout()
    # savefig("{}.pdf".format(title))
    plt.show()


def plot_ratio(df, a, b, country="Total"):
    """
    Plot and calculate the ratio of column `a` and `b` in the dataframe
    `df` with respect to given `country`.
    
    Args:
        df(pandas.DataFrame): Dataframe to be processed.
        a(str): The nominator column of the ratio.
        b(str): The denominator column of the ratio.
        country(str): Country to plot the statistics, default: showing
            statistics of all countries.
    """
    assert isinstance(df, pd.DataFrame)
    assert isinstance(a, str) and a in df.columns
    assert isinstance(b, str) and b in df.columns
    assert isinstance(country, str)

    subset = df[df['country'] == country] if country != "Total" else df

    subset = subset.groupby('category')[a].agg('sum') / \
             subset.groupby('category')[b].agg('sum')

    subset = subset.sort_values(ascending=False).reset_index()
    subset.columns = ['category', 'ratio']

    plt.subplots(figsize=(10, 15))
    sns.barplot(x="ratio",
                y="category",
                data=subset,
                label="{}-{} Ratio".format(a, b),
                color="b")

    plt.title("{}_{}_{}_ratio_category".format(country, a, b))
    plt.tight_layout()


def plot_publish_info(df, country="Total", pattern="%Y-%m-%d %H:%M:%S"):
    """
    Plot publish time (weekday and hour in a day) w.r.t. number of
    trending videos in the given pandas.DataFrame `df`.
    
    Args:
        df(pandas.DataFrame): Dataframe to be processed.
        country(str): Country to plot the statistics, default: showing
            statistics of all countries.
        pattern(str): Datetime pattern in `df`.
    """
    assert isinstance(df, pd.DataFrame)
    assert isinstance(country, str)
    assert isinstance(pattern, str)
    
    subset = df[df['country'] == country] if country != "Total" else df
    # Convert to datetime obkect
    subset = subset[subset["publish_time"].notnull()]
    subset["publish_time"] = subset["publish_time"].apply(
        lambda x: datetime.datetime.strptime(str(x), pattern))
    
    # Create columns for published weekday and hour for analysis
    # Abbreviation of weekday string: Mon, Tue, Wed, Thu, Fri, Sat, Sun
    delta = 0
    if country == "US":
        delta = 0
    if country == "IN":
        delta = 5
    if country == "RU":
        delta = 3
    # Change the time zone of each country
    subset["pub_weekday"] = subset["publish_time"].apply(lambda x: x.strftime('%a'))
    subset["pub_hour"] = subset["publish_time"].apply(lambda x: (x.hour+delta) % 24)

    # Publish week day
    data = subset["pub_weekday"].value_counts().to_frame().reset_index()\
             .rename(columns={
                         "index": "pub_weekday",
                         "pub_weekday": "# of videos"
                     })

    fig, ax = plt.subplots()
    sns.barplot(x="pub_weekday",
                y="# of videos",
                data=data,
                palette=sns.color_palette([
                    '#003f5c', '#374c80', '#7a5195', '#bc5090', '#ef5675',
                    '#ff764a', '#ffa600'
                ], n_colors=7),
                ax=ax)

    ax.set(xlabel="Publishing Day", ylabel="# of videos")

    title = "{} Publish day v.s. # of videos".format(country)

    plt.title(title)
    plt.tight_layout()
    plt.show()

    # Publish hour
    data = subset["pub_hour"].value_counts().to_frame().reset_index()\
            .rename(columns={
                        "index": "pub_hour",
                        "pub_hour": "# of videos"
                    })
    
    fig, ax = plt.subplots()
    sns.barplot(x="pub_hour",
                y="# of videos",
                data=data,
                palette=sns.cubehelix_palette(n_colors=24),
                ax=ax)
    ax.set(xlabel="Publishing Hour", ylabel="# of videos")
    
    title = "{} Publish hour v.s. # of videos".format(country)

    plt.title(title)
    plt.tight_layout()
    plt.show()


def plot_ranking(df, country="Total"):
    """
    Plot the ranking of video categories in the given dataframe.
    
    Args:
        df(pandas.DataFrame): Dataframe to be processed.
        country(str): Country to plot the statistics, default: showing
            statistics of all countries.
    """
    assert isinstance(df, pd.DataFrame)
    assert isinstance(country, str)

    subset = df[df['country'] == country] if country != "Total" else df
    
    subset = df['category'].value_counts().reset_index()
    
    plt.figure(figsize=(15, 10))
    sns.set_style("whitegrid")

    ax = sns.barplot(x=subset['category'],
                     y=subset['index'],
                     data=subset,
                     orient='h')

    plt.xlabel("# of Videos") 
    plt.ylabel("Categories")
    
    title = "Catogories of trending videos in {}"\
            .format("all countries" if country == "Total" else country)
    plt.title(title)
    plt.tight_layout()


def plot_duration_on_list(df, country, file, xrot=70, showcloud=False):
    """
    Plot duration of videos on trending list
    
    Args:
        df(pandas.DataFrame): Dataframe to be processed.
        country(str): Country to plot the statistics, default: showing
            statistics of all countries.
        file(str): Path to the category *.json file
        xrot(int): Rotation for xlabel.
    """
    assert isinstance(df, pd.DataFrame)
    assert isinstance(country, str)
    assert isinstance(file, str) and os.path.exists(file)
    assert isinstance(xrot, int)

    with open(file, 'r') as f:
        items = json.load(f)['items']
        items_id = list(map(lambda x: x['id'], items))
        items_title = list(map(lambda x: x['snippet']['title'], items))
        categories = {int(k):v for k, v in zip(items_id, items_title)}
    
    _subset = df[df["country"] == country].reset_index()

    subset = pd.DataFrame(_subset)
    subset["trending_date"] = subset["trending_date"].astype(str)

    _subset["category_id"] = _subset["category_id"].astype(int)

    for i in _subset.category_id.unique():
        # Remove entries with category_id not in given dictionary
        if i not in categories.keys():
            subset.drop(subset.loc[subset.category_id == i].index,
                        inplace=True)
    
    # Use number as index
    subset.set_index(np.arange(0, subset.shape[0]), inplace=True)
    
    # Convert columns to time format using pd-inference
    subset.publish_time = pd.to_datetime(subset.publish_time,
                                         infer_datetime_format=True)

    subset.trending_date = pd.to_datetime(subset.trending_date,
                                          format='%Y-%m-%d',
                                          infer_datetime_format=True,
                                          utc=True)

    duration, begin = {}, {}
    # Calculate the duration of each video
    I = pd.Index(subset.video_id)
    for vid in I.unique():
        t = I.get_value(subset.trending_date, vid)
        if isinstance(t, pd.datetime):
            duration[vid] = 1
            begin[vid] = t
        else:
            duration[vid] = t.shape[0]
            begin[vid] = t.min()
    
    # Fill in the duration
    subset['duration'] = subset.video_id.map(duration)
    
    # Calculate mean duration for videos in each category
    mean_period = subset.groupby(['category_id']).duration.mean()

    plt.figure(figsize=(9.0, 6.0), facecolor='white')
    x = list(range(mean_period.shape[0]))
    
    plt.plot(x, mean_period, 'o-')
    xlabel = mean_period.index.map(categories)
    plt.xticks(x, labels=xlabel, rotation=xrot)
    plt.ylim(bottom=1)
    plt.grid(True)

    title = "Average days on trending list in {}".format(country)
    plt.xlabel("Category")
    plt.ylabel("Duration (days)")
    plt.title(title)
    plt.tight_layout()
    plt.show()
    
    # Wordcloud
    if showcloud:
        tags = subset.loc[subset.tags.str.find('none') == -1].tags
        data = {}
        for x in tags:
            words = x.split('|')
            for w in words:
                w = w.lower().replace('\"', '')
                data[w] = data.get(w, 0) + 1

        cloud = wordcloud.WordCloud(background_color='black')
        cloud.generate_from_frequencies(data)

        plt.figure(figsize=(9.0, 6.0))
        plt.imshow(cloud)
        plt.axis('off')

        title = "Wordcloud for {}".format(country)
        plt.title(title)
        plt.tight_layout(pad=0.0)
