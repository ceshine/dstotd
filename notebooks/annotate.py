
# coding: utf-8

# In[2]:


from datetime import datetime
import json
import os

import pandas as pd
import numpy as np
import requests
import plotly
import plotly.graph_objs as go
from bs4 import BeautifulSoup
from tqdm import tqdm_notebook
from joblib import Parallel, delayed


os.environ["http_proxy"] = "http://192.168.199.10:11233"
os.environ["https_proxy"] = "http://192.168.199.10:11233"

get_ipython().magic('matplotlib inline')
plotly.offline.init_notebook_mode(connected=True)


# In[3]:


get_ipython().magic('load_ext watermark')
get_ipython().magic('watermark')
get_ipython().magic('watermark -p plotly,tqdm,joblib,pandas,numpy,requests')


# ## Read in the json file

# In[3]:


with open("../tweets.json") as f:
    tweets = json.load(f)
tweets[:2]


# In[4]:


for t in tweets:
    t["date"] = datetime.strptime(t["date"], "%Y-%m-%d").date()
tweets[:2]    


# In[5]:


df_tweets = pd.DataFrame(tweets)
print(df_tweets.shape[0])
df_tweets = df_tweets.drop_duplicates("tid")
print(df_tweets.shape[0])
df_tweets.set_index("tid", inplace=True)
df_tweets.head()


# In[6]:


df_tweets[df_tweets.no_conversation == True].head()


# ## Assign Topic when Appropriate

# ### With Only Headline 

# In[7]:


df_only_headline = df_tweets[(df_tweets["sub-headline"].str.len() == 0) & (df_tweets["tags"].apply(
    lambda x: len(set(["misc", "learning", "tool", "dataviz", "research"]).intersection(set(x))) == 0
))]
headline_date_count = df_only_headline.groupby(["headline", "date"]).size()
headline_date_count[headline_date_count > 1]


# In[8]:


df_only_headline[df_only_headline["tags"].apply(lambda x: "nlp" in set(x))].groupby(["headline", "date"]).size()


# In[9]:


df_only_headline[df_only_headline["tags"].apply(lambda x: "rstats" in set(x))].groupby(["headline", "date"]).size()


# In[10]:


headline_unique_date_count = headline_date_count.groupby("headline").size()
headline_unique_date_count[headline_unique_date_count > 1]


# In[11]:


blacklist = set(["NLP", "Notables", "rstats"])
headlines = list(set(headline_date_count[headline_date_count > 1].index.get_level_values(0)) - blacklist)
for headline in headlines:
    tweet_idx = df_tweets[df_tweets.headline == headline].index
    assert tweet_idx.shape[0] > 1
    df_tweets.loc[tweet_idx[1:], "parent_tid"] = tweet_idx[0]
df_tweets[~df_tweets.parent_tid.isnull()].head()


# ### Sub-headline

# In[12]:


df_tweets[df_tweets["headline"] == "#UseR2018"]


# In[13]:


df_sub_headline = df_tweets[(df_tweets["sub-headline"].str.len() > 0)]
sub_headline_date_count = df_sub_headline.groupby(["headline", "sub-headline", "date"]).size()
sub_headline_date_count[sub_headline_date_count > 1].index.get_level_values(1)


# In[14]:


blacklist = ["#rstats", "rstats", "Python", "Datasets", "GANs", "AI", "Causal Models", "Thoughts"]
sub_headline_date_count = sub_headline_date_count[
    (sub_headline_date_count > 1) & ([
       x not in blacklist for x in sub_headline_date_count.index.get_level_values(1).tolist()])]
sub_headline_date_count


# In[15]:


headlines = sub_headline_date_count.index.get_level_values(0).tolist()
sub_headlines = sub_headline_date_count.index.get_level_values(1).tolist()
for headline, sub_headlines in zip(headlines, sub_headlines):
    tweet_idx = df_tweets[
        (df_tweets.headline == headline) & (df_tweets["sub-headline"] == sub_headlines)].index
    assert tweet_idx.shape[0] > 1
    df_tweets.loc[tweet_idx[1:], "parent_tid"] = tweet_idx[0]
df_tweets[~df_tweets.parent_tid.isnull() & (df_tweets["sub-headline"].str.len() > 0)].head()


# In[16]:


df_tweets[~df_tweets.parent_tid.isnull()].shape[0] / df_tweets.shape[0] * 100


# In[17]:


df_tweets.shape[0]


# ### Dump Results

# In[18]:


df_tweets.reset_index().to_pickle("../tweets_extended.pkl")


# ## Visualize

# In[19]:


tweets_by_date = df_tweets.groupby("date").size()
data = [
    go.Bar(
        x=tweets_by_date.index.tolist(),
        y=tweets_by_date.values,
        marker=dict(
            color=[
                'rgba(222,45,38,0.8)' if d.weekday() > 4 else 'rgba(204,204,204,1)'
                for d in tweets_by_date.index.tolist()
            ]
        ),
        name='Tweets'       
    )  
]
layout = go.Layout(
    title='# of Collected Tweets per Day',
    autosize=False,
    width=900,
    height=300,
    margin=go.Margin(
    #     l=50,
    #     r=50,
      b=50,
      t=50,
    #     pad=4
    )
)
fig = go.Figure(data=data, layout=layout)
plotly.offline.iplot(fig)


# ## Collect oembed

# In[20]:


endpoint = "https://api.twitter.com/1.1/statuses/oembed.json?id={tid}&omit_script=0&maxwidth=500"
res = requests.get(endpoint.format(tid=df_tweets.index[0]))
res


# In[21]:


res = res.json()
res


# In[22]:


bs = BeautifulSoup(res["html"], "html.parser")
" ".join([str(x) for x in bs.find("blockquote").children])


# In[23]:


def collect_oembed(tid):
    res = requests.get(endpoint.format(tid=tid)).json()
    if "html" not in res:
        print(tid, res)
        return None
    res = res["html"]
    bs = BeautifulSoup(res, "html.parser")
    return " ".join([str(x) for x in bs.find("blockquote").children])


# In[24]:


oembeds = Parallel(n_jobs=8)(delayed(collect_oembed)(tid) for tid in tqdm_notebook(df_tweets.index.tolist()))


# In[25]:


df_tweets["oembed"] = oembeds
df_tweets.sample()


# In[26]:


df_tweets[df_tweets.oembed.isnull()]


# In[27]:


## Dump Results
df_tweets.reset_index().to_pickle("../tweets_extended.pkl")


# ## Collect More Information

# In[39]:


df_tweets = pd.read_pickle("../tweets_extended.pkl").set_index("tid")


# In[46]:


from credentials import *
import twitter
if os.environ.get("LOCAL", False):
    PROXIES = dict(http='socks5://192.168.199.10:12133',
                   https='socks5://192.168.199.10:12133')
else:
    PROXIES = None
API = twitter.Api(
    consumer_key=CONSUMER_KEY,
    consumer_secret=CONSUMER_SECRET,
    access_token_key=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET,
    tweet_mode="extended",
    proxies=PROXIES,
    sleep_on_rate_limit=True
)


# In[47]:


API.InitializeRateLimit()


# In[48]:


API.rate_limit.get_limit("/statuses/show/:id")


# In[49]:


tmp = API.GetStatus(df_tweets.index[0])


# In[25]:


tmp.full_text


# In[26]:


tmp.created_at_in_seconds


# In[27]:


tmp.user


# In[53]:


oembed_null = df_tweets.oembed.isnull()
if "author" in df_tweets.columns:
    author_null = df_tweets.author.isnull()
else:
    author_null = True
    
for i in tqdm_notebook(df_tweets.index.tolist()):
    if oembed_null[i]:
        continue
    if author_null is not True and not author_null[i]:
        continue
    status = API.GetStatus(i)
    df_tweets.loc[i, "author"] = status.user.screen_name
    df_tweets.loc[i, "timestamp"] = status.created_at_in_seconds
    df_tweets.loc[i, "reply_to_tid"] = status.in_reply_to_status_id
    df_tweets.loc[i, "reply_to_sname"] = status.in_reply_to_screen_name


# In[54]:


print(df_tweets.reset_index().drop_duplicates("tid").shape[0])
df_tweets.shape[0]


# In[56]:


df_tweets.sample(10)


# In[57]:


## Dump Results
df_tweets.reset_index().to_pickle("../tweets_extended.pkl")


# In[ ]:




