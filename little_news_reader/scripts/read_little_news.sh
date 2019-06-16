#!/bin/bash

LITTLE_NEWS_HOME='/opt/little_news/src/'
cd ${LITTLE_NEWS_HOME}/little_news
export PYTHONPATH=${PYTHONPATH}:${LITTLE_NEWS_HOME}
exec /home/pi/.virtualenvs/little_news/bin/python2.7 read_little_news.py "$@"