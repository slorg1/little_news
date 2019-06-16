from types import StringType
import re
import socket

from BeautifulSoup import BeautifulSoup
import feedparser

from little_news.feed.AbstractFeedReader import AbstractFeedReader


class RssFeedParser(AbstractFeedReader):
    """
        Implementation of a feed parser using L{feedparser}
    """
    socket.setdefaulttimeout(10)

    def get_items(self, url, last_modified, etag):
        assert isinstance(url, StringType)
        assert last_modified is None or isinstance(last_modified, StringType)
        assert etag is None or isinstance(etag, StringType)

        assert url
        assert last_modified is None or last_modified
        assert etag is None or etag

        d = feedparser.parse(url, etag=etag, modified=last_modified)

        if not d.has_key('status'):
            raise ValueError('Could not read status from the feed')

        if d.status in (304, 301):
            return etag, last_modified, d.status, str(d.href), (x for x in tuple()) # no changes

        if 'etag' in d:
            etag = str(d.etag)
        else:
            etag = None

        if 'modified' in d:
            lm = str(d.modified)
        else:
            lm = None
        return etag, lm, d.status, str(d.href), RssFeedParser.__items_iterator(d)

    @staticmethod
    def __items_iterator(d):
        """
            Iterator yielding the format described in L{AbstractFeedReader.get_items}
            @type d: feedparser.FeedParserDict
        """
        assert isinstance(d, feedparser.FeedParserDict)

        cleanser = RssFeedParser.__CLEANSER
        for entry in d.entries:
            guid = entry.get('id')
            guid = guid if guid else None
            title = entry.get('title')
            title = cleanser.sub('', BeautifulSoup(title).text) if title else None
            description = entry.get('description')
            description = cleanser.sub('', BeautifulSoup(description).text) if description else None
            yield guid, title, description


    __CLEANSER = re.compile(r'(&(?:(?:nbsp)|(?:quot)|(?:#160));)', re.IGNORECASE)
