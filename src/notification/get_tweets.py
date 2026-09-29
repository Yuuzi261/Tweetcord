from typing import Optional

from tweety.types import Tweet

from src.notification.date_comparator import date_comparator


def _is_match(tweet: Tweet, user_id: str) -> bool:
    if user_id is not None:
        author_id = getattr(tweet.author, 'id', None)
        if author_id is not None and str(author_id) == str(user_id):
            return True
    return False

async def get_tweets(tweets: list[Tweet], user_id: str = None, last_tweet_at: str = None) -> Optional[list[Tweet]]:
    """
    Filters tweets based on user_id, and the last recorded tweet timestamp.
    """
    if not last_tweet_at or not tweets:
        return None

    matched_tweets = [tweet for tweet in tweets if _is_match(tweet, user_id) and date_comparator(tweet.created_on, last_tweet_at) == 1]

    if matched_tweets:
        return sorted(matched_tweets, key=lambda x: x.created_on)
    else:
        return None

