from flask import render_template, Blueprint, flash, redirect, url_for, make_response
from flask_login import login_required

from app.models import Bot, TwitterAccount, Account
from app.forms import AddTwitterAccountForm, AddBotAccountForm
from app.controllers import get_twitter_id


main_blueprint = Blueprint("main", __name__)


@main_blueprint.route("/")
def index():
    new_follow_form = AddTwitterAccountForm()
    new_bot_form = AddBotAccountForm()
    bot = Bot.query.first()
    bot_accounts = Account.query.all()
    twitter_accounts = TwitterAccount.query.all()
    return render_template(
        "index.html",
        bot=bot,
        new_follow_form=new_follow_form,
        new_bot_form=new_bot_form,
        accounts=twitter_accounts,
        bot_accounts=bot_accounts
    )


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


@main_blueprint.route("/add_twitter_account", methods=["GET", "POST"])
@login_required
def add_twitter_account():
    form = AddTwitterAccountForm()
    if form.validate_on_submit():
        username = form.username.data
        if TwitterAccount.query.filter(TwitterAccount.username == username).first():
            flash("Username is already added", "warning")
            return redirect(url_for("main.index"))
        twitter_id = get_twitter_id(username)
        if not twitter_id:
            flash("Username is invalid. Please check data and try again", "danger")
            return redirect(url_for("main.index"))
        twitter_account = TwitterAccount(
            username=form.username.data, twitter_id=twitter_id
        )
        twitter_account.save()
        flash("Username successfully added", "success")
    return redirect(url_for("main.index"))


@main_blueprint.route("/delete_twitter_account/<int:twitter_id>")
@login_required
def delete_twitter_account(twitter_id):
    account = TwitterAccount.query.filter(
        TwitterAccount.twitter_id == twitter_id
    ).first()
    if not account:
        flash("No account associated with this id. Please try again", "danger")
        return redirect(url_for("main.index"))
    account.delete()
    flash("Account successfully deleted", "info")
    return redirect(url_for("main.index"))


@main_blueprint.route("/add_bot_account", methods=["GET", "POST"])
@login_required
def add_bot_account():
    form = AddBotAccountForm()
    if form.validate_on_submit:
        account = Account.query.filter(Account.role == form.role.data).first()
        if not account:
            account = Account(role=form.role.data)
        account.name = form.name.data
        account.consumer_key = form.consumer_key.data
        account.consumer_secret = form.consumer_secret.data
        account.access_token = form.access_token.data
        account.access_token_secret = form.access_token_secret.data
        account.save()
        flash(f"{form.role.data} account has been sucessfully updated", "success")
        return redirect(url_for("main.index"))
    flash("Failed to update, please check your data and try again")
    return redirect(url_for("main.index"))
