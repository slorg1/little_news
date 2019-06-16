from exceptions import NotImplementedError


class AbstractPlayer(object):
    """

    """

    def play(self, feed_entries):
        raise NotImplementedError()