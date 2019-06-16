from types import StringType, UnicodeType
import logging
import subprocess
import tempfile
import uuid

from little_news.tts.AbstractTTSManager import AbstractTTSManager


class PicoTTSManager(AbstractTTSManager):
    """
        Implementation of the L{little_news.tts.AbstractTTSManager} using C{pico2wave}
    """

    LANGUAGES = frozenset(
                           (
                            'en-US',
                            'en-GB',
                            'fr-FR',
                            ))
    """ Set of supported languages """

    def __init__(self, language):
        """
             Constructor
        """
        super(PicoTTSManager, self).__init__(language)
        cmd_path = subprocess.check_output(['which', 'pico2wave'])
        if not cmd_path:
            raise EnvironmentError("Could not find pico2wave")
        self.__tts_command = (cmd_path.strip(), '-l', self._language, '-w',)
        cmd_path = subprocess.check_output(['which', 'avconv'])
        if not cmd_path:
            raise EnvironmentError("Could not find avconv")
        self.__wav_2_mp3_command = cmd_path.strip()

    def get_supported_languages(self):
        return PicoTTSManager.LANGUAGES

    def read(self, text, target_file):
        """
            In addition, this implementation will create a '.wav' temporary file.
        """
        assert isinstance(text, (StringType, UnicodeType))
        assert text
        assert isinstance(target_file, StringType), type(target_file)
        assert target_file
        assert target_file.endswith('mp3')

        handle = None # keep the handle to the temp file to have it available while we use it outside of python
        try:
            handle = tempfile.NamedTemporaryFile(suffix='.wav', prefix='little_news_' + str(uuid.uuid4()))
            path_2_wav = handle.name
            subprocess.check_call(
                                  self.__tts_command + (path_2_wav, text.encode("utf-8"),)
                                  )
            subprocess.check_call((self.__wav_2_mp3_command,)
                                  + PicoTTSManager.__TO_MP3_CMD[:PicoTTSManager.__INPUT_FILE_INDEX]
                                  + (path_2_wav,)
                                  + PicoTTSManager.__TO_MP3_CMD[PicoTTSManager.__INPUT_FILE_INDEX:] + (target_file,))
        except:
            PicoTTSManager.__LOGGER.error('Error reading text using pico2wave', exc_info=1)
            raise
        finally:
            if handle is not None:
                handle.close()

    __INPUT_FILE_INDEX = 4
    """
        Index for the L{PicoTTSManager.__TO_MP3_CMD} command letting us know where to set the input file.
    """

    __TO_MP3_CMD = (
                    '-loglevel', 'quiet', # no logs
                    '-y', # force override
                    '-i' , # input
                    '-af', "volume=volume=2:precision=double", # triple the volume... I'm deaf
                    '-codec:a', 'libmp3lame' , '-f' , 'mp3', # use mp3
                    '-flags' , 'pass2', '-qscale' , '1', # get super quality
                    '-b', '128k', # bit rate
                    )
    __LOGGER = logging.getLogger(__name__)
