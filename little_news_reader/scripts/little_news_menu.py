import functools
import json
import subprocess
import sys, os
import time


sys.path.append('/opt/simple_menu/src/')

from simple_menu.builders.AbstractMenuBuilder import AbstractMenuBuilder
from simple_menu.builders.PropertiesMenuBuilder import PropertiesMenuBuilder
from simple_menu.handlers.MenuHandler import MenuHandler
import Adafruit_CharLCD as LCD

# Show some basic colors.
RED = (1.0, 0.0, 0.0)
GREEN = (0.0, 1.0, 0.0)
BLUE = (0.0, 0.0, 1.0)
YELLOW = (1.0, 1.0, 0.0)
CYAN = (0.0, 1.0, 1.0)
MAGENTA = (1.0, 0.0, 1.0)
WHITE = (1.0, 1.0, 1.0)

message_old = LCD.Adafruit_CharLCDPlate.message # monkey patch this thing to wrap automatically
def message(self, msg):
    if len(msg) > 16:
        for msg in msg.split('\n'):
            msg = msg[:16] + '\n' + msg[16:]
            message_old(self, msg)
    else:
        message_old(self, msg)

LCD.Adafruit_CharLCDPlate.message = message
lcd = LCD.Adafruit_CharLCDPlate()


def shutdown(lcd):
    lcd.message('Extinction des feux!')
    try:
        subprocess.check_call(('sudo', 'shutdown', '-h', 'now'))
        lcd.set_backlight(0.)
    except e:
        lcd.message('Error: %s' % str(e))

def get_ip(lcd):
    try:
        ip = subprocess.check_output(('hostname', '-I'))
        lcd.message('Mon I.P. est:\n%s' % str(ip))
    except:
        lcd.message('Error reading IP')
#         raise

def update_feeds(lcd):
    lcd.message("C'est parti!!!")
    lcd.set_color(*RED)
    try:
        subprocess.check_call(('bash', '/opt/little_news/scripts/update_little_news.sh'))
    except:
        lcd.message('Error: could not execute little news')
    lcd.set_color(*BLUE)

def read_feed(lcd, feed_name):
    lcd.message("Blabla!!!")
    lcd.set_color(*RED)
    try:
        subprocess.check_call(('bash', '/opt/little_news/scripts/read_little_news.sh', feed_name))
    except:
        lcd.message('Error: could not execute little news')
    lcd.set_color(*BLUE)

builder = PropertiesMenuBuilder('/opt/little_news/conf/menu.properties')
callbacks = {
               'UPDATE_FEED':functools.partial(update_feeds, lcd),
               'SHUTDOWN':functools.partial(shutdown, lcd),
               'GET_IP':functools.partial(get_ip, lcd),
           }
try:
    feed_names = json.loads(
                            subprocess.check_output(('bash',
                                                     '/opt/little_news/scripts/list_little_news_feeds.sh'))
                            )
    feed_sections = []
    READ_FEED = 'READ_FEED'
    for idx, feed_name in enumerate(feed_names):
        callback = READ_FEED + str(idx)
        feed_sections.append((feed_name, callback,))
        callbacks[callback] = functools.partial(read_feed, lcd, feed_name)

    menu = builder.build({'section_list_feeds':feed_sections})

    m_h = MenuHandler(menu, callbacks)

    # Make list of button value, text, and backlight color.
    buttons = ((LCD.SELECT, m_h.forward),
                (LCD.LEFT, m_h.back),
                (LCD.UP, m_h.previous),
                (LCD.DOWN, m_h.next),
                (LCD.RIGHT, m_h.forward),
              )
    lcd.set_color(*BLUE)
    lcd.message(m_h.get_current_location())

    while True:
        # Loop through each button and check if it is pressed.
        for idx, button in enumerate(buttons):
            if lcd.is_pressed(button[0]):
                lcd.clear()
                try:
                    ret = button[1]()
                except:
                    ret = 'Unknown error'

                if ret is not None:
                    lcd.message(ret)

        time.sleep(0.1)
except:
    lcd.message('Error: could not execute little news')


