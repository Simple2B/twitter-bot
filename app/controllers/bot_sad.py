import os
import time

import tweepy

from app.models import Account, Bot, TwitterAccount, Keyword, ExclusionKeyword
from app.logger import log


class BotSad():

    class Worker():

        def __init__(self, consumer_key, consumer_secret, access_token, access_token_secret, bot_sad):
            self.bot_sad = bot_sad
            auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
            auth.set_access_token(access_token, access_token_secret)
            api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
            try:
                api.verify_credentials()
                self.api = api
                log(log.INFO, "API Created")
            except tweepy.TweepError as error:
                log(log.ERROR, "[%s]", error.reason)
                raise error

        class Stream_Listener(tweepy.StreamListener):
            """Defines the tweet status and error state"""

            def __init__(self, api, bot_sad):
                self.api = api
                self.me = api.me()
                self.bot_sad = bot_sad
                self.keywords = [key.word for key in Keyword.query.all()]
                self.exclusion_keywords = [key.word for key in ExclusionKeyword.query.all()]

            def on_status(self, tweet):
                """Checks the status of the tweet. Mark it as favourite if not already done it and retweet if not already
                retweeted.

                :param tweet: tweet from listening to the stream
                """
                if tweet.in_reply_to_status_id is not None or tweet.user.id == self.me.id:
                    # This tweet is a reply or I'm its author so ignore it
                    return
                if not tweet.retweeted and 'RT @' not in tweet.text:
                    # Since Twitter API provides only approximate match to the track keywords,
                    # further filtering required in order to get precise match for the tweets
                    if [keyword for keyword in self.keywords if(keyword in tweet.text)]:
                        try:
                            # tweet.retweet()
                            # currently printing results to console for testing purposes
                            log(log.INFO, 'News Account RT: [%s]', tweet.text)
                        except tweepy.TweepError as error:
                            log(log.ERROR, "[%s]", error.reason)
                    else:
                        if [keyword for keyword in self.exclusion_keywords if(keyword in tweet.text)]:
                            self.bot_sad.retweet(tweet.id)
                        else:
                            try:
                                # tweet.retweet()
                                # currently printing results to console for testing purposes
                                log(log.INFO, 'News Account RT: [%s]', tweet.text)
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

        def listen(self):
            list_of_accounts = [str(account.twitter_id) for account in TwitterAccount.query.all()]
            self.stream_listener = self.Stream_Listener(api=self.api, bot_sad=self.bot_sad)
            self.stream = tweepy.Stream(auth=self.api.auth, listener=self.stream_listener)
            self.stream.filter(follow=list_of_accounts, languages=["en"])
            # list_of_words = [key.word for key in Keyword.query.all()]
            # self.stream.filter(track=list_of_words, languages=["en"])

        def retweet_exclusion(self, tweet_id):
            """ Method to retweet a tweet """
            # self.api.retweet(tweet_id)
            log(log.INFO, 'Exclusion Account RT: [%d]', tweet_id)

    def __init__(self):

        bot = Bot.query.first()
        if not bot:
            bot = Bot()
        bot.pid = os.getpid()
        log(log.INFO, "Bot PID: [%d]", bot.pid)
        bot.status = Bot.StatusType.active
        bot.action = Bot.ActionType.start
        bot.save()

        accounts = Account.query.all()
        for account in accounts:
            if account.role == Account.RoleType.news:
                self.worker_news = BotSad.Worker(
                    consumer_key=account.consumer_key,
                    consumer_secret=account.consumer_secret,
                    access_token=account.access_token,
                    access_token_secret=account.access_token_secret,
                    bot_sad=self
                )
            elif account.role == Account.RoleType.exclusion:
                self.worker_exclusion = BotSad.Worker(
                    consumer_key=account.consumer_key,
                    consumer_secret=account.consumer_secret,
                    access_token=account.access_token,
                    access_token_secret=account.access_token_secret,
                    bot_sad=self
                )

    def listen(self):
        log(log.INFO, 'News Account started streaming')
        self.worker_news.listen()

    def retweet(self, tweet_id):
        self.worker_exclusion.retweet_exclusion(tweet_id)
