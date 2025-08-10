from typing import Optional

from tweety.types import Tweet

from src.notification.date_comparator import date_comparator


async def get_tweets(tweets: list[Tweet], username: str, last_tweet_at: str) -> Optional[list[Tweet]]:
    """
    Filters tweets based on the last recorded tweet timestamp.
    This function no longer performs database operations.
    """
    if not last_tweet_at:
        return None

    tweets = [tweet for tweet in tweets if tweet.author.username == username and date_comparator(tweet.created_on, last_tweet_at) == 1]

    if tweets:
        return sorted(tweets, key=lambda x: x.created_on)
    else:
        return None
