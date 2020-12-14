from app.models import User, Bot


def register(username, email="username@test.com", password='password'):
    user = User(username=username, email=email, password=password)
    user.save()
    return user.id


def login(client, username, password="password"):
    return client.post('/login', data=dict(
        user_id=username,
        password=password
    ), follow_redirects=True)


def logout(client):
    return client.get("/logout", follow_redirects=True)


def bot_manager(client):
    """Start Twitter Stream bot manager."""
    bot = Bot.query.first()
    msg = ''
    # Initial bot activation
    if bot.status == Bot.StatusType.active:
        if bot.action == Bot.ActionType.stop:
            bot.status = Bot.StatusType.disabled
            msg = 'Bot previous status - [active]; current status - [disabled]'
        elif bot.action == Bot.ActionType.restart:
            msg = 'Bot is restarting'
        else:
            msg = 'No action required'
    else:
        if bot.action == Bot.ActionType.start:
            bot.status = Bot.StatusType.active
            msg = 'Bot previous status - [disabled]; current status - [active]'
        elif bot.action == Bot.ActionType.restart:
            msg = 'Bot is restarting'
        else:
            msg = 'No action required'
    return msg
