import logging.config
import sqlite3
import sys

from little_news.TTSRssFeedReader import TTSRssFeedReader
from little_news.news.PyGamePlayer import PyGamePlayer


logging.config.fileConfig('conf/logging.conf')
logger = logging.getLogger('little_news')
logger.debug('Logging setup!')

if __name__ == '__main__':

    if len(sys.argv) == 1:
        feed_name = None
    elif len(sys.argv) == 2:
        feed_name = str(sys.argv[1])
    else:
        raise ValueError("Bad parameters")

    conn = sqlite3.connect(# @UndefinedVariable
                           '/opt/little_news/data/data.sqlite',
                           isolation_level=None) # @UndefinedVariable

    TTSRssFeedReader(PyGamePlayer()).read(conn, feed_name, 1)
    conn.close()

