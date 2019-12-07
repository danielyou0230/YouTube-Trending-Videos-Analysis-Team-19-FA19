import datetime
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


def plot_correlation(df, country, brief=[]):
    """
    
    Args:
        df(pandas.DataFrame):
        country(str):
        brief(list[str]):
    
    Return:
        None
    """
    assert isinstance(country, str)
    subset = df[df["country"] == country]
    # subset.corr()

    labels = [
        x.replace('_', ' ').title() for x in list(
            subset.select_dtypes(include=['number', 'bool']).columns.values)
    ]

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(subset.corr(),
                annot=True,
                xticklabels=labels,
                yticklabels=labels,
                cmap=sns.cubehelix_palette(as_cmap=True),
                ax=ax)

    postfix = "_brief" if brief else ""
    title = "{}_corr_heatmap{}".format(country, postfix)

    # Make the figure more readable
    plt.xticks(rotation=30)
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
    
    Args:
        df(pd.DataFrame):
        a(str):
        b(str):
        tag(str):
    """
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
    
    subset = df[df['country'] == country] if country != "Total" else df
    # Convert to datetime obkect
    subset["publish_time"] = subset["publish_time"].apply(
        lambda x: datetime.datetime.strptime(str(x), pattern))
    
    # Create columns for published weekday and hour for analysis
    # Abbreviation of weekday string: Mon, Tue, Wed, Thu, Fri, Sat, Sun
    subset["pub_weekday"] = subset["publish_time"].apply(lambda x: x.strftime('%a'))
    subset["pub_hour"] = subset["publish_time"].apply(lambda x: x.hour)
    # df.drop(labels='publish_time', axis=1, inplace=True)

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
#     plt.yticks(rotation=90)
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
    plt.yticks(rotation=90)
    plt.title(title)
    plt.tight_layout()
    plt.show()