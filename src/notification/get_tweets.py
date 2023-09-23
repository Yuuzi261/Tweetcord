def get_tweets(tweets, username):
    tweets = [tweet for tweet in tweets if tweet.author.username == username]
    lastest_tweet = sorted(tweets, key=lambda x: x.created_on, reverse=True)[0]
    return lastest_tweet