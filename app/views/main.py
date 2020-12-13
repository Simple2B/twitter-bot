from flask import render_template, Blueprint, flash, redirect, url_for, make_response
from flask_login import login_required

from app.controllers import start_bot, stop_bot
from app.models import Bot

main_blueprint = Blueprint("main", __name__)


@main_blueprint.route("/")
def index():
    bot = Bot.query.first()
    return render_template("index.html", bot=bot)


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
