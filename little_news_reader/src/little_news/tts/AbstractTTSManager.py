from types import StringType, UnicodeType

class AbstractTTSManager(object):
    """
        Abstract implementation for a TTS reader, takes text and reads it into a specific output audio format.
    """

    def __init__(self, language):
        """
            Initializes this TTS manager with supported language.

            @precondition: language in self.get_supported_languages()
        """
        assert language in self.get_supported_languages()

        self.__language = language

    def get_supported_languages(self):
        """
            Returns a set of the languages supported by this TTS manager.

            @rtype: frozenset

            @postcondition: len(return) > 0
        """
        raise NotImplementedError()

    def read(self, text, target_file):
        """
            Reads the given L{text} and outputs it to the given L{target_file} location. The target file
            will be overwritten if it already exists.

            @type text: StringType
            @type target_file: StringType or UnicodeType

            @precondition: len(text) > 0
            @precondition: len(target_file) > 0
        """
        assert isinstance(text, (StringType, UnicodeType))
        assert text
        assert isinstance(target_file, StringType)
        assert target_file

        raise NotImplementedError()


    def _language(): # @NoSelf
        def fget(self):
            return self.__language
        return locals()

    _language = property(**_language())
    """
        Getter:
        =======
        Gets the language for this entity

        @rtype: StringType

        @postcondition: len(return) > 0

        Setter:
        =======
        Not settable.
    """
