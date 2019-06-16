from types import StringType, IntType
import logging
import os
import sqlite3

from little_news.TTSRssFeedCrawler import TTSRssFeedCrawler
from little_news.data.FeedDAO import FeedDAO
from little_news.data.FeedEntityDAO import FeedEntityDAO
from little_news.news.AbstractPlayer import AbstractPlayer


class TTSRssFeedReader(object):
    """
        Reader used to read all L{feeds<little_news.data.FeedDAO.FeedDAO.Feed>}s and save the processed
        items using L{little_news.data.FeedEntityDAO.FeedEntityDAO}.
    """

    AUDIO_ROOT_FOLDER = '/opt/little_news/audio/'
    """ Location of the root directory to save the audio files. """

    def __init__(self, player):
        """
             Intializes this reader with a L{player}.

             @type player: AbstractPlayer
        """
        assert isinstance(player, AbstractPlayer)

        self.__player = player

    def read(self, connection, feed_name=None, count=None):
        """
            Implements the class contract.

            @param connection: connection used to save the data
            @type connection: sqlite3.Connection
            @param feed_name: (optional) the name of the feed to play, if C{None} plays all feeds.
            @param count: number of elements to read.

            @precondition: feed_name is None or isinstance(feed_name, StringType)
            @precondition: feed_name is None or len(feed_name) > 0
            @precondition: count is None or isinstance(count, IntType)
            @precondition: count is None or count > 0
        """
        assert isinstance(connection, sqlite3.Connection) # @UndefinedVariable
        assert count is None or isinstance(count, IntType)
        assert count is None or count > 0

        c = connection.cursor()
        if not feed_name:
            assert feed_name is None
            feeds = list(FeedDAO.find_all(c,))
        else:
            isinstance(feed_name, StringType)
            feed = FeedDAO.find_by_name(c, feed_name)
            if not feed:
                TTSRssFeedReader.__LOGGER.warn('%s cannot be found as a feed name' % (feed_name))
                return
            feeds = (feed,)

        AUDIO_ROOT_FOLDER = TTSRssFeedCrawler.AUDIO_ROOT_FOLDER

        if not os.path.exists(AUDIO_ROOT_FOLDER):
            assert not feeds
            TTSRssFeedReader.__LOGGER.info('%s cannot be found, no feeds have been crawled' % (AUDIO_ROOT_FOLDER))
            return

        read_count = 0
        for feed in feeds:
            TTSRssFeedReader.__LOGGER.debug("Reading %s", str(feed))
            name_audio = feed.name_audio
            entities = tuple(FeedEntityDAO.find_all_by_feed_and_is_read(c, feed, False))
            for entity in entities:
                self.__player.play(name_audio, (entity,))
                FeedEntityDAO.mark_as_read(c, entity)
                # Save (commit) the changes
                connection.commit()
                read_count += 1
                if count is not None and read_count == count:
                    return

    __LOGGER = logging.getLogger(__name__)
