#!/user/bin/env python
import os

import click

from app import create_app, db, models, forms
from app.models import User, Bot
from app.logger import log
from app.controllers import run_bot, start_bot, stop_bot, restart_bot


app = create_app()
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin")


def add_bot():
    db.session.add(Bot())
    db.session.commit()


def add_admin():
    db.session.add(
        User(
            username=ADMIN_USERNAME,
            email="test_account@gmail.com",
            password=ADMIN_PASSWORD,
            activated=True,
        )
    )
    db.session.commit()


def _init_db():
    db.create_all()
    add_admin()
    add_bot()


# flask cli context setup
@app.shell_context_processor
def get_context():
    """Objects exposed here will be automatically available from the shell."""
    return dict(app=app, db=db, models=models, forms=forms)


@app.cli.command()
@click.confirmation_option(prompt="Delete all data from database tables?")
def reset_db():
    """Reset the current database."""
    db.drop_all()
    _init_db()


@app.cli.command()
def create_db():
    """Create the configured database."""
    db.create_all()


@app.cli.command()
@click.confirmation_option(prompt="Drop all database tables?")
def drop_db():
    """Drop the current database."""
    db.drop_all()


@app.cli.command()
def bot():
    """Start Twitter Stream bot."""
    log(log.DEBUG, 'Starting bot')
    run_bot()


@app.cli.command()
@click.option('--start/--stop', default=True)
def manager(start):
    """Start Twitter Stream bot manager."""
    if start:
        bot = Bot.query.first()

        # Initial bot activation
        if not bot:
            log(log.INFO, 'No bot found...')
            start_bot()

        if bot.status == Bot.StatusType.active:
            if bot.action == Bot.ActionType.stop:
                log(log.INFO, 'Terminating bot with PID [%d]', bot.pid)
                stop_bot()
            elif bot.action == Bot.ActionType.restart:
                log(log.INFO, 'Restarting bot with PID [%d]', bot.pid)
                restart_bot()
            else:
                log(log.INFO, 'Bot with PID [%d] is already running', bot.pid)
                return
        else:
            if bot.action == Bot.ActionType.start:
                log(log.INFO, 'Attempting to start bot')
                start_bot()
            elif bot.action == Bot.ActionType.restart:
                log(log.INFO, 'Restarting bot with PID [%d]', bot.pid)
                restart_bot()
            else:
                log(log.INFO, 'Bot is disabled')
                return
    else:
        stop_bot()


if __name__ == "__main__":
    app.run()
