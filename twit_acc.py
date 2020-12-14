import tweepy


consumer_key = "LxykA9YyxgVjVIGHQLCGDmLd4"
consumer_secret = 'NrnkbqN5JxAOWnI8hqAf54bNTg4V6NuoKMFJNpnX6Sg4BEbqAV'
access_token = '358912326-A0RkPBbFLQOFGa4NFUdjmMXNDTJZzoHvaD9f4J3a'
access_token_secret = 'EY9ZnhkYdWcbzbFf7Nqp05lvjzQkdzpwtDfFSQYIZI4xN'

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

api.verify_credentials()

user = api.get_user('@realdonaldtrump')
