import os
import time

import tweepy

from app.models import Bot
from app.logger import log

def create_api():
    """This function collects the consumer and access keys, creates an api object and returns the authenticated api
    object.

    :return: authenticated api object
    """
    consumer_key = os.environ.get('CONSUMER_KEY', 'No consumer_key provided')
    consumer_secret = os.environ.get('CONSUMER_SECRET', 'No consumer_secret provided')
    access_token = os.environ.get('ACCESS_TOKEN', 'No access_token provided')
    access_token_secret = os.environ.get('ACCESS_TOKEN_SECRET', 'No access_token_secret provided')

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
        raise error
    print("API created")
    return api


class Stream_Listener(tweepy.StreamListener):
    """Defines the tweet status and error state

    """

    def __init__(self, api):
        self.api = api
        self.me = api.me()

    def on_status(self, tweet):
        """Checks the status of the tweet. Mark it as favourite if not already done it and retweet if not already
        retweeted.

        :param tweet: tweet from listening to the stream
        """
        if tweet.in_reply_to_status_id is not None or tweet.user.id == self.me.id:
            # This tweet is a reply or I'm its author so, ignore it
            return
        if not tweet.favorited:
            # Mark it as Liked, since we have not done it yet
            try:
                tweet.favorite()
                print('Stream favorited tweet:', tweet.text)
            except tweepy.TweepError as error:
                print(error)
        if not tweet.retweeted:
            # Retweet, since we have not retweeted it yet
            try:
                tweet.retweet()
                print('Stream retweeted tweet:', tweet.text)
            except tweepy.TweepError as error:
                print(error)

    def on_error(self, status_code):
        """When encountering an error while listening to the stream, return False if `status_code` is 420 and print
        the error.

        :param status_code:
        :return: False when `status_code` is 420 to disconnect the stream.
        """
        log(log.DEBUG, os.environ.get('ACCESS_TOKEN'))
        if status_code == 420:
            # returning False in on_error disconnects the stream
            return False
        elif status_code == 429:
            time.sleep(900)
        else:
            print(tweepy.TweepError, status_code)


def run_bot(follow=None, keyword=None):
    """Main method to initialize the api, create a Stream_Listener object to track tweets based on certain keywords and
    follow tweet owners and the mentors.
    """
    bot = Bot.query.first()
    if not bot:
        bot = Bot()
    bot.pid = os.getpid()
    bot.save()

    if not follow:
        # TODO get followers list from DB?
        pass

    if not keyword:
        # TODO get keywords from Google Sheets
        pass

    api = create_api()
    my_stream_listener = Stream_Listener(api)
    my_stream = tweepy.Stream(auth=api.auth, listener=my_stream_listener)

    # , is_async=True, languages=["en"]
    my_stream.filter(track=keyword, follow=follow)





if __name__ == '__main__':
    # "224115510", "2998698451", "743086819"
    # "#keywords"
    follow_list = []
    keywords = []
    run_bot(follow_list, keywords)
