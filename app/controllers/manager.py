#!./.venv/bin/python

import os
import time
import subprocess

from app.models import Bot
from app.logger import log


def check_pid(pid):
    """ Check For the existence of a unix pid. """
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    else:
        return True


def start_bot():
    log(log.INFO, "Atempting to start bot")
    bot = Bot.query.first()
    if bot:
        if bot.status == Bot.StatusType.active:
            if check_pid(bot.pid):
                log(log.INFO, "Process [%d] is alredy running", bot.pid)
                return 1
            bot.status = Bot.StatusType.disabled
            bot.save()
    # run bot
    # cmd = "source .venv/bin/activate; flask bot"
    # subprocess.call(cmd, shell=True, executable='/bin/bash')
    # subprocess.Popen(["source", ".venv/bin/python"])
    os.system('flask bot &')
    time.sleep(5)
    bot = Bot.query.first()
    if not bot:
        log(log.ERROR, "No bot created")
        return 2
    if not bot.pid:
        log(log.ERROR, "Bot pid not found")
        return 3
    if not check_pid(bot.pid):
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
        if bot.pid and check_pid(bot.pid):
            os.kill(bot.pid, 9)
    else:
        log(log.INFO, "Bot process is not running")
