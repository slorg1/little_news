from types import StringType, UnicodeType, ListType, TupleType, BooleanType
import collections
import sqlite3
from little_news.data.FeedDAO import FeedDAO


class FeedEntityDAO(object):
    """
        Data access object handling the persistence and retrieval of L{FeedEntity.FeedEntity}.
    """

    FeedEntity = collections.namedtuple('FeedEntity', (
                                                          'id',
                                                          'feed_id',
                                                          'guid',
                                                          'title',
                                                          'title_audio',
                                                          'description_audio',
                                                          'read',
                                                          ))
    """
        Entity representing a single entry in
    """

    @staticmethod
    def create_table(cursor):
        assert isinstance(cursor, sqlite3.Cursor) # @UndefinedVariable
        cursor.execute("""
            CREATE TABLE feed_entries (
                    id INTEGER PRIMARY KEY,
                    feed_id INTEGER NOT NULL,
                    guid TEXT NOT NULL,
                    title TEXT NOT NULL,
                    title_audio TEXT NOT NULL,
                    description_audio TEXT NOT NULL,
                    read INTEGER NOT NULL
                );
            """)

    @staticmethod
    def find_all_by_feed_and_is_read(cursor, feed, is_read):
        """
            Finds and returns all L{FeedEntityDAO.FeedEntity} records for the given L{feed}.
            The records are ordered by L{FeedEntityDAO.FeedEntity.id} descendant.

            @type feed: FeedDAO.Feed
            @param is_read: if C{True} the records returned will all have as have M{1} L{read<FeedEntityDAO.
            FeedEntity.read>}
            @type is_read: BooleanType
        """
        assert isinstance(feed, FeedDAO.Feed)
        assert isinstance(is_read, BooleanType)

        return (
               FeedEntityDAO.FeedEntity(idx, feed_id, guid, title, title_audio, description_audio, read)
               for idx, feed_id, guid, title, title_audio, description_audio, read  in cursor.execute(
                                 ("SELECT id, feed_id, guid, title, title_audio, description_audio, read "
                                 "FROM feed_entries "
                                 "WHERE feed_id = ? AND "
                                 + ("read > 0 " if is_read else "read == 0 ") +
                                 "ORDER BY id DESC"), (feed.id,)))

    @staticmethod
    def find_all_by_feed(cursor, feed):
        assert isinstance(feed, FeedDAO.Feed)
        return (
               FeedEntityDAO.FeedEntity(idx, feed_id, guid, title, title_audio, description_audio, read)
               for idx, feed_id, guid, title, title_audio, description_audio, read  in cursor.execute(
                                 "SELECT id, feed_id, guid, title, title_audio, description_audio, read "
                                 "FROM feed_entries "
                                 "WHERE feed_id = ? ORDER BY id DESC", (feed.id,)))

    @staticmethod
    def mark_as_read(cursor, feed_entity):
        """
            Updates the database and adds a L{read<FeedEntityDAO.FeedEntity.read>} count for the given
            L{feed_entiy} record.

            @type feed_entity: FeedEntityDAO.FeedEntity
        """
        assert isinstance(feed_entity, FeedEntityDAO.FeedEntity)
        cursor.execute(
                      "UPDATE feed_entries SET read = read + 1 WHERE id = ?",
                      (
                       feed_entity.id,
                       )
                      )

    @staticmethod
    def delete(cursor, feed, items_to_delete):
        """

            @type items_to_delete: ListType or TupleType or collections.deque

            @precondition: len(items_to_delete) > 0
        """
        assert isinstance(items_to_delete, (ListType , TupleType , collections.deque))
        assert items_to_delete

        ids_to_delete = ','.join(map(str, (x.id for x in items_to_delete)))

        if ids_to_delete:
            return cursor.execute(
                                  "DELETE FROM feed_entries WHERE feed_id = ? AND id IN (%s)" % (ids_to_delete),
                                  (
                                   feed.id,
                                   )
                                  ).rowcount
        return 0

    @staticmethod
    def insert(cursor, feed, guid, title, title_audio_path, description_audio_path):
        assert isinstance(cursor, sqlite3.Cursor) # @UndefinedVariable
        assert isinstance(feed, FeedDAO.Feed)
        assert isinstance(guid, StringType)
        assert isinstance(title, UnicodeType)
        assert isinstance(title_audio_path, StringType)
        assert isinstance(description_audio_path, StringType)
        assert guid
        assert title
        assert title_audio_path
        assert description_audio_path

        cursor.execute("INSERT INTO feed_entries "
                        "(feed_id, guid, title, title_audio, description_audio, read) "
                        "VALUES (?, ?, ?, ?, ?, 0);", (
                                                    feed.id,
                                                    guid,
                                                    title,
                                                    title_audio_path,
                                                    description_audio_path,
                                                    ))

