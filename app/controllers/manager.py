#!./.venv/bin/python

import os
import time

from app.models import Bot
from app.logger import log


def start_bot():
    log(log.INFO, "Atempting to start bot")
    bot = Bot.query.first()
    if bot:
        if bot.status == Bot.StatusType.active:
            if bot.is_active:
                log(log.INFO, "Process [%d] is alredy running", bot.pid)
                return 1
            bot.status = Bot.StatusType.disabled

            bot.save()
    # run bot
    os.system('flask bot &')
    time.sleep(5)
    bot = Bot.query.first()
    if not bot:
        log(log.ERROR, "No bot created")
        return 2
    if not bot.pid:
        log(log.ERROR, "Bot pid not found")
        return 3
    if not bot.is_active:
        log(log.ERROR, "Bot has terminated")
        return 4
    log(log.INFO, "Bot started with pid [%d]", bot.pid)
    bot.status = Bot.StatusType.active
    bot.save()
    return 0


def stop_bot():
    log(log.INFO, "Attempting to stop bot")
    bot = Bot.query.first()
    if bot and bot.status == Bot.StatusType.active:
        log(log.INFO, "Shutdown bot process [%d]", bot.pid)
        if bot.pid and bot.is_active:
            os.kill(bot.pid, 9)
            log(log.INFO, "Stopped bot process [%d]", bot.pid)
            bot.status = Bot.StatusType.disabled
            bot.action = Bot.ActionType.stop
            bot.save()
    else:
        log(log.INFO, "Bot process is not running")


def restart_bot():
    log(log.INFO, "Attempting to restart bot")
    stop_bot()
    start_bot()
