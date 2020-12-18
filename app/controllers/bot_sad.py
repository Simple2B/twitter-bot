import tweepy

from app.models import Account
from app import log


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
            """Defines the tweet status and error state

            """

            def __init__(self, api, bot_sad):
                self.api = api
                self.me = api.me()
                self.bot_sad = bot_sad
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
                    # Since Twitter API provides only approximate match to the track keywords,
                    # further filtering required in order to get precise match for the tweets
                    if [keyword for keyword in self.keywords if(keyword in tweet.text)]:
                        try:
                            tweet.retweet()
                            # currently printing results to console for testing purposes
                            # print('Stream retweeted tweet:', tweet.text)
                        except tweepy.TweepError as error:
                            log(log.ERROR, "[%s]", error.reason)
                    else:
                        self.bot_sad.repost(tweet)


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

        def retweet():
            pass

    def retweet(self, tweet):
        worker_exclusion.update_status(tweet)

    def __init__(self):
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
        
        self.worker_news.listen()
        
