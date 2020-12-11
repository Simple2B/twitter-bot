from flask import render_template, Blueprint, flash, redirect, url_for
from flask_login import login_required

from app.controllers import start_bot, stop_bot
from app.models import Bot

main_blueprint = Blueprint('main', __name__)


@main_blueprint.route('/')
def index():
    bot = Bot.query.first()
    return render_template('index.html', bot=bot)


@main_blueprint.route('/start_bot_stream')
@login_required
def run_bot():
    start_bot()
    bot = Bot.query.first()
    if bot and bot.status == Bot.StatusType.active:
        flash("Bot has successfully started", 'success')
        return redirect(url_for('main.index'))
    flash("An error occured while starting bot. Plesase try again", 'danger')
    return redirect(url_for('main.index'))


@main_blueprint.route('/stop_bot_stream')
@login_required
def terminate_bot():
    stop_bot()
    bot = Bot.query.first()
    if bot and bot.status == Bot.StatusType.disabled:
        flash("Bot has successfully stopped", 'success')
        return redirect(url_for('main.index'))
    flash("An error occured while stopping bot. Plesase try again", 'danger')
    return redirect(url_for('main.index'))
