import os

import tweepy

from app.models import Account, TwitterAccount
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


def get_twitter_id(username: str):
    api = create_api()
    try:
        user = api.get_user(username)
        return user.id
    except tweepy.TweepError as error:
        log(log.ERROR, "[%s]", error.reason)


def validate_bot_accounts():
    workers = Account.query.all()
    if len(workers) < 2:
        log(log.ERROR, 'Bots are not set up. Make sure you have both News and Exclusion bots')
        return False
    if not Account.query.filter(Account.role == Account.RoleType.news).first():
        log(log.ERROR, 'News Account is not set up. Make sure you have set up News Account')
        return False
    if not Account.query.filter(Account.role == Account.RoleType.exclusion).first():
        log(log.ERROR, 'Exclusion Account is not set up. Make sure you have set up Exclusion Account')
        return False
    if not TwitterAccount.query.all():
        log(log.ERROR, 'Twitter Accounts to be followed are not set up')
        return False
    keywords, exclusion_keywords = parse_gsheet()
    if not keywords:
        log(log.ERROR, 'Keywords are not set up. Update keyword list and try again.')
        return False
    if not exclusion_keywords:
        log(log.ERROR, 'Exclusion keywords are not set up. Update exclusion list and try again.')
        return False
    return True
