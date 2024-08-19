import os
import sqlite3
from src.notification.date_comparator import date_comparator

def get_tweets(tweets, username):
    
    conn = sqlite3.connect(os.path.join(os.getenv('DATA_PATH'), 'tracked_accounts.db'))
    cursor = conn.cursor()
    last_tweet_at = cursor.execute('SELECT lastest_tweet FROM user WHERE username = ?', (username,)).fetchone()[0]
    conn.close()
    
    tweets = [tweet for tweet in tweets if tweet.author.username == username and date_comparator(tweet.created_on, last_tweet_at) == 1]
    
    if tweets != []: return sorted(tweets, key=lambda x: x.created_on)
    else: return None