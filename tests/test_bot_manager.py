import pytest

from app import create_app, db
from app.models import Bot

from .utils import register, login, bot_manager


@pytest.fixture
def client():
    app = create_app(environment="testing")
    app.config["TESTING"] = True

    with app.test_client() as client:
        app_ctx = app.app_context()
        app_ctx.push()
        db.drop_all()
        db.create_all()
        register('sam')
        login(client, 'sam')
        yield client
        db.session.remove()
        db.drop_all()
        app_ctx.pop()


def test_manager_routes(client):
    """Test basic bot manager endpoints."""
    bot = Bot(status=Bot.StatusType.active, action=Bot.ActionType.stop)
    bot.save()
    response = client.get('/start_bot_stream', follow_redirects=True)
    assert b'Bot has successfully started' in response.data
    assert bot.action == Bot.ActionType.start

    response = client.get('/stop_bot_stream', follow_redirects=True)
    assert b'Bot has successfully stopped' in response.data
    assert bot.action == Bot.ActionType.stop


def test_manager_logic(client):
    """Test manager signals logic."""
    bot = Bot(status=Bot.StatusType.disabled, action=Bot.ActionType.stop)
    bot.save()
    client.get('/start_bot_stream', follow_redirects=True)

    response = bot_manager(client)
    assert bot.status == Bot.StatusType.active
    assert 'Bot previous status - [disabled]; current status - [active]' in response

    client.get('/stop_bot_stream', follow_redirects=True)
    response = bot_manager(client)
    assert bot.status == Bot.StatusType.disabled
    assert 'Bot previous status - [active]; current status - [disabled]' in response

    client.get('/start_bot_stream', follow_redirects=True)
    bot_manager(client)

    res = client.get('/restart_bot_stream', follow_redirects=True)
    assert res.status_code == 200
    response = bot_manager(client)
    assert bot.status == Bot.StatusType.active and bot.action == Bot.ActionType.restart
    assert 'Bot is restarting' in response
