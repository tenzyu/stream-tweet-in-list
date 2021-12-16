import tweepy


class Twitter(tweepy.API):
    def __init__(
        self, consumer_key, consumer_secret, access_token, access_token_secret
    ):
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        super().__init__(auth)
