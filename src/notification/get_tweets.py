def get_tweets(tweets, username):
    tweets = [tweet for tweet in tweets if tweet.author.username == username]
    if tweets != []:
        return sorted(tweets, key=lambda x: x.created_on, reverse=True)[0]
    else:
        return None