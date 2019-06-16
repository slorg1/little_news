from types import StringType
import collections
import sqlite3


class FeedDAO(object):
    """
        Data access object handling the persistence and retrieval of L{FeedDAO.FeedEntity}.
    """

    Feed = collections.namedtuple('Feed', (
                                          'id',
                                          'last_modified',
                                          'etag',
                                          'url',
                                          'name',
                                          'name_audio',
                                          )
                                  )
    """
        Entity representing a single entry in
    """

    @staticmethod
    def create_table(cursor):
        assert isinstance(cursor, sqlite3.Cursor) # @UndefinedVariable
        cursor.execute("""
            CREATE TABLE feed
            (
                id INTEGER PRIMARY KEY,
                last_modified TEXT,
                etag TEXT,
                url TEXT NOT NULL,
                "name" TEXT NOT NULL,
                "name_audio" TEXT NOT NULL
            );
        """)

    @staticmethod
    def find_all(cursor,):
        return (
                FeedDAO.Feed(idx, str(lm), str(etag), str(url), name.encode('utf-8'), str(name_audio))
                  for idx, lm, etag, url, name, name_audio in cursor.execute(
                                                           "SELECT id, last_modified, etag, url, name, name_audio FROM feed;"
                                                            )
               )

    @staticmethod
    def find_by_name(cursor, name):
        """
            Finds and returns a single L{FeedDAO.Feed} record whose L{name<FeedDAO.Feed.name>} matches L{name}.
            If none could be found, return C{None}.

            @type name: StringType
            @precondition: len(name) > 0

            @postcondition: return is None or isinstance(return, FeedDAO.Feed,)
        """
        assert isinstance(name, StringType)
        assert name

        return next((
                FeedDAO.Feed(idx, str(lm), str(etag), str(url), name.encode('utf-8'), str(name_audio))
                  for idx, lm, etag, url, name, name_audio in cursor.execute(
                                               "SELECT id, last_modified, etag, url, name, name_audio "
                                               "FROM feed "
                                               "WHERE name = ?;", (name,)
                                                            )
               ), None)


    @staticmethod
    def update(cursor, feed, last_modified, etag):
        assert isinstance(cursor, sqlite3.Cursor) # @UndefinedVariable
        assert etag is None or isinstance(etag, StringType)
        assert etag is None or etag
        assert last_modified is None or isinstance(last_modified, StringType)
        assert last_modified is None or last_modified

        cursor.execute("UPDATE feed SET etag = ?, last_modified = ? WHERE id = ?", (
                                                                                    etag,
                                                                                    last_modified,
                                                                                    feed.id,
                                                                                    ))
        return FeedDAO.Feed(feed.id, last_modified, etag, feed.url, feed.name, feed.name_audio)


    @staticmethod
    def update_url(cursor, feed, url):
        assert isinstance(cursor, sqlite3.Cursor) # @UndefinedVariable
        assert isinstance(url, StringType)
        assert url
        cursor.execute("UPDATE feed SET url = ? WHERE id = ?", (
                                                                url,
                                                                feed.id,
                                                                ))
        return FeedDAO.Feed(feed.id, feed.last_modified, feed.etag, url)




