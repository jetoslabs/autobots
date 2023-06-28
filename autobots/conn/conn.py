from functools import lru_cache

from autobots.conn.openai.openai import OpenAI
from autobots.conn.selenium.selenium import Selenium
from autobots.conn.stability.stability import Stability
from autobots.conn.unsplash.unsplash import Unsplash
from autobots.core.settings import Settings, get_settings


class Conn:

    def __init__(self, settings: Settings):
        # setting up OpenAI
        self.open_ai = OpenAI()
        self.selenium = Selenium()
        self.stability = Stability()
        self.unsplash = Unsplash()


@lru_cache
def get_conn(settings: Settings = get_settings()) -> Conn:
    return Conn(settings)
