from itertools import chain
import sqlite3

import pandas as pd
import numpy as np

DB_PATH = "tweets.db"


def get_conn():
    return sqlite3.connect("tweets.db")


def create_tables():
    with get_conn() as conn:
        c = conn.cursor()
        # Tag Table
        c.execute('''
            CREATE TABLE tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            );
        ''')
        # Tweet Table
        c.execute('''
            CREATE TABLE tweets (
                id UNSIGNED BIG INT PRIMARY KEY,
                timestamp INTEGER NOT NULL,
                block_quote TEXT NOT NULL,
                author TEXT NOT NULL,
                no_conversation TINYINT DEFAULT 0,
                parent_id UNSIGNED BIG INT,
                reply_to_tid UNSIGNED BIG INT,
                reply_to_sname TEXT,
                FOREIGN KEY(parent_id) REFERENCES tweets(id)
            );
        ''')
        # Tag-Tweet Table
        c.execute('''
            CREATE TABLE tweet_tag_assoc (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tweet_id UNSIGNED BIG INTEGER,
                tag_id INTEGER,
                CONSTRAINT unique_tag UNIQUE (tag_id, tweet_id)
                FOREIGN KEY(tag_id) REFERENCES tags(id),
                FOREIGN KEY(tweet_id) REFERENCES tweets(id)
            );
        ''')

        conn.commit()


def insert_tags():
    tags = [(None, x) for x in list(set(chain.from_iterable(DF.tags)))]
    with get_conn() as conn:
        c = conn.cursor()
        c.execute('DELETE FROM tags;')
        c.executemany('INSERT INTO tags VALUES (?, ?)', tags)

        conn.commit()


def insert_tweets():
    tweets = [(
        row["tid"], row["timestamp"], row["oembed"],
        row["author"], row["no_conversation"], row["parent_tid"],
        row["reply_to_tid"], row["reply_to_sname"]
    ) for _, row in DF.iterrows() if row["oembed"] is not None]
    with get_conn() as conn:
        c = conn.cursor()
        c.execute('DELETE FROM tweets;')
        c.executemany(
            'INSERT INTO tweets VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
            tweets)

        conn.commit()


def associate_tweet_and_tags():
    with get_conn() as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM tags')
        tag_dict = dict((name, id_) for id_, name in c.fetchall())
        print(tag_dict)
        assoc = []
        for _, row in DF.iterrows():
            for tag in set(row["tags"]):
                assoc.append((None, row["tid"], tag_dict[tag]))
        c.execute('DELETE FROM tweet_tag_assoc;')
        c.executemany(
            'INSERT INTO tweet_tag_assoc VALUES (?, ?, ?);',
            assoc
        )

        conn.commit()


if __name__ == "__main__":
    create_tables()
    DF = pd.read_pickle("tweets_extended.pkl")
    insert_tags()
    insert_tweets()
    associate_tweet_and_tags()
