from tweety.types import Tweet


def is_match_type(tweet: Tweet, enable_type: str):
    tweet_type = 0 if tweet.is_retweet else 1 if tweet.is_quoted else -1
    return tweet_type == -1 or enable_type[tweet_type] == '1'


def is_match_media_type(tweet: Tweet, media_type: str):
    return media_type == '11' or (media_type == '10' and len(tweet.media) == 0) or (media_type == '01' and len(tweet.media) > 0)
