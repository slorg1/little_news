import logging.config
import sqlite3

from little_news.TTSRssFeedCrawler import TTSRssFeedCrawler
from little_news.feed.RssFeedParser import RssFeedParser
from little_news.tts.PicoTTSManager import PicoTTSManager


logging.config.fileConfig('conf/logging.conf')
logger = logging.getLogger('little_news')
logger.debug('Logging setup!')

if __name__ == '__main__':
    tts_manager = PicoTTSManager(
                                  'fr-FR'
                                 )
    conn = sqlite3.connect(# @UndefinedVariable
                           '/opt/little_news/data/data.sqlite',
                           isolation_level=None) # @UndefinedVariable
    TTSRssFeedCrawler(tts_manager, RssFeedParser()).crawl(conn)
    conn.close()

