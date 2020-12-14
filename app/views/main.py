from flask import render_template, Blueprint, flash, redirect, url_for, make_response
from flask_login import login_required

from app.models import Bot, TwitterAccount
from app.forms import AddTwitterAccountForm
from app.controllers import get_twitter_id


main_blueprint = Blueprint("main", __name__)


@main_blueprint.route("/")
def index():
    form = AddTwitterAccountForm()
    bot = Bot.query.first()
    twitter_accounts = TwitterAccount.query.all()
    return render_template("index.html", bot=bot, form=form, accounts=twitter_accounts)


@main_blueprint.route("/start_bot_stream")
@login_required
def run_bot():
    bot = Bot.query.first()
    if not bot:
        flash("An error occured while starting bot. Plesase try again", "danger")
        return redirect(url_for("main.index"))
    if bot.status == Bot.StatusType.active and bot.action == Bot.ActionType.start:
        flash("Bot is already running", "info")
        return redirect(url_for("main.index"))
    bot.action = Bot.ActionType.start
    bot.save()
    flash("Bot has successfully started", "success")
    return redirect(url_for("main.index"))


@main_blueprint.route("/stop_bot_stream")
@login_required
def terminate_bot():
    bot = Bot.query.first()
    if not bot:
        flash("An error occured while stopping bot. Plesase try again", "danger")
        return redirect(url_for("main.index"))
    bot.action = Bot.ActionType.stop
    bot.save()
    flash("Bot has successfully stopped", "success")
    return redirect(url_for("main.index"))


@main_blueprint.route("/restart_bot_stream")
@login_required
def restart_bot():
    bot = Bot.query.first()
    if not bot:
        flash("An error occured while restarting bot. Plesase try again", "danger")
        return redirect(url_for("main.index"))
    bot.action = Bot.ActionType.restart
    bot.save()
    flash("Bot has successfully restarted", "success")
    return redirect(url_for("main.index"))


@main_blueprint.route("/refresh_bot_status")
@login_required
def refresh_bot_status():
    bot = Bot.query.first()
    if bot.is_active:
        return make_response({"status": "Bot is currently running"}, 200)
    else:
        return make_response({"status": "Bot is currently offline"}, 200)


@main_blueprint.route("/add_twitter_account", methods=['GET', 'POST'])
@login_required
def add_twitter_account():
    form = AddTwitterAccountForm()
    if form.validate_on_submit():
        username = form.username.data
        if TwitterAccount.query.filter(TwitterAccount.username == username):
            flash("Username is already added", "warning")
            return redirect(url_for("main.index"))
        twitter_id = get_twitter_id(username)
        if not twitter_id:
            flash("Username is invalid. Please check data and try again", "danger")
            return redirect(url_for("main.index"))
        twitter_account = TwitterAccount(username=form.username.data, twitter_id=twitter_id)
        twitter_account.save()
        flash("Username successfully added", "success")
    return redirect(url_for("main.index"))
