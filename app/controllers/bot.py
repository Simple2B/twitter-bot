import os
import time

import tweepy

from app.models import Bot, Keyword, TwitterAccount
from app.logger import log
from app.controllers import parse_gsheet


def create_api():
    """This function collects the consumer and access keys, creates an api object and returns the authenticated api
    object.

    :return: authenticated api object
    """
    consumer_key = os.environ.get('CONSUMER_KEY', 'No consumer_key provided')
    log(log.INFO, consumer_key)
    consumer_secret = os.environ.get('CONSUMER_SECRET', 'No consumer_secret provided')
    log(log.INFO, consumer_secret)
    access_token = os.environ.get('ACCESS_TOKEN', 'No access_token provided')
    log(log.INFO, access_token)
    access_token_secret = os.environ.get('ACCESS_TOKEN_SECRET', 'No access_token_secret provided')
    log(log.INFO, access_token_secret)

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

    return authenticate_api(api)


def authenticate_api(api):
    """This function verifies the credentials and returns the authenticated api object

    :param api: api object
    :return: authenticated api object
    :raises TweepError: raised due to an error Twitter Responded with or raised when an API method fails due to hitting
    Twitter’s rate limit.
    """
    try:
        api.verify_credentials()
    except tweepy.TweepError as error:
        log(log.ERROR, "[%s]", error.reason)
        raise error
    log(log.INFO, "API Created")
    return api


class Stream_Listener(tweepy.StreamListener):
    """Defines the tweet status and error state

    """

    def __init__(self, api):
        self.api = api
        self.me = api.me()
        self.keywords = [key.word for key in Keyword.query.all()]

    def on_status(self, tweet):
        """Checks the status of the tweet. Mark it as favourite if not already done it and retweet if not already
        retweeted.

        :param tweet: tweet from listening to the stream
        """
        if tweet.in_reply_to_status_id is not None or tweet.user.id == self.me.id:
            # This tweet is a reply or I'm its author so ignore it
            return
        if not tweet.retweeted and 'RT @' not in tweet.text:
            # Since Twitter API provides only approximate match to the track keywords, further filtering required
            # in order to get precise match for the tweets
            if [keyword for keyword in self.keywords if(keyword in tweet.text)]:
                try:
                    tweet.retweet()
                    # currently printing results to console for testing purposes
                    # print('Stream retweeted tweet:', tweet.text)
                except tweepy.TweepError as error:
                    log(log.ERROR, "[%s]", error.reason)

    def on_error(self, status_code):
        """When encountering an error while listening to the stream, return False if `status_code` is 420 and print
        the error.

        :param status_code:
        :return: False when `status_code` is 420 to disconnect the stream.
        """
        bot = Bot.query.first()
        if status_code == 420:
            # returning False in on_error disconnects the stream
            log(log.ERROR, 'Received [%d] error', status_code)
            bot.status = Bot.StatusType.disabled
            bot.action = Bot.ActionType.restart
            bot.save()
            return False
        elif status_code == 429:
            log(log.ERROR, "Received [%d] error, bot will sleep for 900 sec", status_code)
            time.sleep(900)
        else:
            log(log.ERROR, "[%s], [%d]", tweepy.TweepError.reason, status_code)


def get_twitter_id(username: str):
    api = create_api()
    try:
        user = api.get_user(username)
        return user.id
    except tweepy.TweepError as error:
        log(log.ERROR, "[%s]", error.reason)


def run_bot(keywords=None):
    """
    Main method to initialize the api, create a Stream_Listener object to track tweets based on certain keywords.
    """
    bot = Bot.query.first()
    if not bot:
        bot = Bot()
    bot.pid = os.getpid()
    bot.status = Bot.StatusType.active
    bot.action = Bot.ActionType.start
    bot.save()
    list_of_accounts = [str(account.twitter_id) for account in TwitterAccount.query.all()]

    # if not follow:
    #     # TODO get followers list from DB?
    #     pass

    if not keywords:
        # parse google sheet and save keywords to DB
        keywords = parse_gsheet()

    api = create_api()
    my_stream_listener = Stream_Listener(api)
    my_stream = tweepy.Stream(auth=api.auth, listener=my_stream_listener)

    my_stream.filter(follow=list_of_accounts, languages=["en"])
