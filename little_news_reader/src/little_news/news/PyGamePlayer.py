import pygame
import time
from little_news.news.AbstractPlayer import AbstractPlayer

class PyGamePlayer(AbstractPlayer):
    """

    """

    def play(self, intro, feed_entries):
        assert feed_entries
        pygame.mixer.init(frequency=16000)
        pygame.mixer.music.load(intro)
        pygame.mixer.music.play()

        for entry in feed_entries:
            pygame.mixer.music.queue(entry.title_audio)
            pygame.mixer.music.queue(entry.description_audio)

            while pygame.mixer.music.get_busy():
                time.sleep(2)

        pygame.mixer.quit()
