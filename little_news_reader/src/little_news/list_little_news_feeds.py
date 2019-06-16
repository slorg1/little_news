from __future__ import print_function

import json
import logging.config
import sqlite3

from little_news.data.FeedDAO import FeedDAO


logging.config.fileConfig('conf/logging.conf')
logger = logging.getLogger('little_news')
logger.debug('Logging setup!')

if __name__ == '__main__':

    conn = sqlite3.connect(# @UndefinedVariable
                           '/opt/little_news/data/data.sqlite',
                           isolation_level=None) # @UndefinedVariable

    feed_names = [feed.name for feed in FeedDAO.find_all(conn.cursor())]
    result = json.dumps(feed_names)
    print(result)

    conn.close()

