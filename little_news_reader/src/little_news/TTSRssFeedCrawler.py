from exceptions import IOError
import collections
import logging
import os
import sqlite3
import uuid

from little_news.data.FeedDAO import FeedDAO
from little_news.data.FeedEntityDAO import FeedEntityDAO
from little_news.feed.AbstractFeedReader import AbstractFeedReader
from little_news.tts.AbstractTTSManager import AbstractTTSManager


class TTSRssFeedCrawler(object):
    """
        Crawlers used to process all L{feeds<little_news.data.FeedDAO.FeedDAO.Feed>}s and save the processed
        items using L{little_news.data.FeedEntityDAO.FeedEntityDAO}.

        The items are retrieved by using the L{TTSRssFeedCrawler.feed_reader} and then processed through the
        L{TTSRssFeedCrawler.tts_manager}.
        All audio files created are saved at L{TTSRssFeedCrawler.AUDIO_ROOT_FOLDER}. The location
        is maintained by this crawler:
            - automatically created upon first execution
            - files are removed when read or deemed too old
    """

    AUDIO_ROOT_FOLDER = '/opt/little_news/audio/'
    """ Location of the root directory to save the audio files. """

    def __init__(self, tts_manager, feed_reader):
        """
             Intializes this crawler with a L{tts_manager} and a L{feed_reader}.

             @type tts_manager: AbstractTTSManager
             @type feed_reader: AbstractFeedReader
        """
        assert isinstance(tts_manager, AbstractTTSManager)
        assert isinstance(feed_reader, AbstractFeedReader)

        self.__tts_manager = tts_manager
        self.__feed_reader = feed_reader

    def crawl(self, connection):
        """
            Implements the class contract.

            @param connection: connection used to save the data
            @type connection: sqlite3.Connection
        """
        assert isinstance(connection, sqlite3.Connection) # @UndefinedVariable
        c = connection.cursor()
        feeds = list(FeedDAO.find_all(c,))

        AUDIO_ROOT_FOLDER = TTSRssFeedCrawler.AUDIO_ROOT_FOLDER

        if not os.path.exists(AUDIO_ROOT_FOLDER):
            os.mkdir(AUDIO_ROOT_FOLDER)

        if not os.path.isdir(AUDIO_ROOT_FOLDER):
            raise IOError('%s is not a folder and it could not be created' % (AUDIO_ROOT_FOLDER))

        for feed in feeds:
            TTSRssFeedCrawler.__LOGGER.debug('Crawling %s', str(feed))

            feed_guids = collections.OrderedDict((x.guid, x) for x in FeedEntityDAO.find_all_by_feed(c, feed))

            try:
                etag, last_modified, http_status, url, items = self.__feed_reader.get_items(
                                                                                         feed.url,
                                                                                         feed.last_modified,
                                                                                         feed.etag,
                                                                                         )
                guid = None
                insert_records = collections.deque()
                for guid, title, description in items:
                    try:
                        if guid is None:
                            guid = title.encode('utf-8')
                        else:
                            guid = guid.encode('utf-8')

                        if guid not in feed_guids:
                            TTSRssFeedCrawler.__LOGGER.info('Reading item %s', guid)
                            uniq = str(uuid.uuid4())
                            title_file = '/opt/little_news/audio/lp_%s_%s.mp3' % (uniq, 'title',)
                            self.__tts_manager.read(title, title_file,)
                            desc_file = '/opt/little_news/audio/lp_%s_%s.mp3' % (uniq, 'description',)
                            self.__tts_manager.read(description, desc_file,)
                        else:
                            TTSRssFeedCrawler.__LOGGER.info('Skipping item %s and all after that', guid)
                            break
                    except:
                        TTSRssFeedCrawler.__LOGGER.error('msg', exc_info=1)
                    else:
                        insert_records.append((c, feed, guid, title, title_file, desc_file,))

                for c, feed, guid, title, title_file, desc_file in reversed(insert_records):
                    FeedEntityDAO.insert(c, feed, guid, title, title_file, desc_file)

                self.__delete_old_items(c, feed, feed_guids.values())

                if etag != feed.etag or last_modified != feed.last_modified:
                    FeedDAO.update(c, feed, last_modified, etag)
                if http_status == 301 and url != feed.url:
                    FeedDAO.update_url(c, feed, url)

            except ValueError:
                TTSRssFeedCrawler.__LOGGER.error('Should be fine', exc_info=1)


            # Save (commit) the changes
            connection.commit()

    def tts_manager(): # @NoSelf
        def fget(self):
            return self.__tts_manager
        def fset(self, value):
            assert isinstance(value, type)
            self.__tts_manager = value
        return locals()

    tts_manager = property(**tts_manager())
    """
        Getter:
        =======
        Gets the tts manager for this entity

        @rtype: AbstractTTSManager

        Setter:
        =======
        Not settable
    """

    def feed_reader(): # @NoSelf
        def fget(self):
            return self.__feed_reader
        return locals()

    feed_reader = property(**feed_reader())
    """
        Getter:
        =======
        Gets the feed reader for this entity

        @rtype: AbstractFeedReader

        Setter:
        =======
        Not settable
    """

    def __delete_old_items(self, c, feed, feed_entities):
        """
            Deletes any feed entities found in L{feed_entities} that are found after the first
            L{FeedEntityDAO.FeedEntity.read} item.
            This method will keep at least one read item to have something to match against on the next run.
            The feed entities are expected to be orders in L{FeedEntityDAO.FeedEntity.id} descending order.

            @type c: sqlite3.Cursor
            @type feed_guids: DictType
            @param feed: the parent L{feed} for the entities
            @type feed: FeedDAO.Feed

            @precondition: all(isinstance(FeedEntityDAO.FeedEntity, feed_entities))
            @precondition: all(f.feed_id == feed.id for f in feed_entities)
            @precondition: all(feed_entities[idx].id < feed_entities[idx+1].id for idx in xrange(0, len(feed_entities)-1))
        """
        assert isinstance(c, sqlite3.Cursor) # @UndefinedVariable
        assert isinstance(feed, FeedDAO.Feed)
        assert isinstance(feed_entities, collections.Sequence), type(feed_entities)

        do_delete = False
        items_to_delete = collections.deque()
        prev_id = None
        for item in feed_entities:
            assert feed.id == item.feed_id
            assert prev_id > item.id or prev_id is None
            prev_id = item.id
            if not do_delete:
                if item.read:
                    do_delete = True
            else:
                assert do_delete is True
                for s in (item.title_audio, item.description_audio):
                    try:
                        os.remove(s)
                    except OSError as e:
                        if 'No such file' in e.strerror:
                            pass
                        else:
                            TTSRssFeedCrawler.__LOGGER.info('Cannot delete: %s from feed id %d', item.guid, feed.id, exc_info=1)
                            break
                    except:
                        TTSRssFeedCrawler.__LOGGER.info('Cannot delete: %s from feed id %d', item.guid, feed.id, exc_info=1)
                        break
                else:
                    # if all deletion were successful enough
                    items_to_delete.append(item)

        if do_delete and len(items_to_delete) > 1:
            items_to_delete.popleft() # keep 1 (newest) to have something to match if we read it all
            row_count = FeedEntityDAO.delete(c, feed, items_to_delete)
            TTSRssFeedCrawler.__LOGGER.info('Deleted %d items for feed %s', row_count, feed.id)
        else:
            assert do_delete is False or len(items_to_delete) <= 1

            TTSRssFeedCrawler.__LOGGER.info('Deleted no items for feed id %d', feed.id)


    __LOGGER = logging.getLogger(__name__)
