from flask import render_template, Blueprint, flash
from flask_login import login_required

from app.controllers import parse_gsheet, start_bot, stop_bot
from app.models import Bot

main_blueprint = Blueprint('main', __name__)


@main_blueprint.route('/')
def index():
    keywords = parse_gsheet()
    bot = Bot.query.first()
    return render_template('index.html', keywords=keywords, bot=bot)


@main_blueprint.route('/start_bot_stream')
@login_required
def run_bot():
    start_bot()
    bot = Bot.query.first()
    if bot and bot.status == Bot.StatusType.active:
        flash("Bot has successfully started", 'success')
        return render_template('index.html', bot=bot)
    flash("An error occured while starting bot. Plesase try again", 'danger')
    return render_template('index.html', bot=bot)


@main_blueprint.route('/stop_bot_stream')
@login_required
def terminate_bot():
    stop_bot()
    bot = Bot.query.first()
    if bot and bot.status == Bot.StatusType.disabled:
        flash("Bot has successfully stopped", 'success')
        return render_template('index.html', bot=bot)
    flash("An error occured while stopping bot. Plesase try again", 'danger')
    return render_template('index.html', bot=bot)
