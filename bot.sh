#!/bin/bash
# Let's call this script venv.sh
WORK_DIR=~/twitter-bot
cd $WORK_DIR
source .venv/bin/activate
flask manager
#comment