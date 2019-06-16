
class AbstractFeedReader(object):
    """
        Abstract implementation for feed reader. It provides a basic interface for reading feeds (atom & RSS).
    """

    def get_items(self, url, last_modified, etag):
        """
            Returns a tuple of:
            C{tuple<etag, last_modified, item_generator}

            Where:
                - C{etag}: etag of the feed (string)
                - C{last_modified}: last modified date  of the feed in the understood format (string)
                - C{item_generator}: iterates through each item of the feed and produces the index, the title
                and the description of the item.
                Format:
                C{tuple<idx, title, description>}

                Where:
                    - idx: is the index (string) of the item (in the feed: guid is provided) or (or C{None}, never empty)
                    - title: is the title of the entry (or C{None}, never empty)
                    - description: is the description of the entry (or C{None}, never empty)

        @type url: StringType
        @precondition: len(url) > 0

        @precondition: last_modified is None or isinstance(last_modified, StringType)
        @precondition: last_modified is None or last_modified
        @precondition: etag is None or isinstance(etag, StringType)
        @precondition: etag is None or etag

        """
        raise NotImplementedError()


    __slots__ = tuple()
