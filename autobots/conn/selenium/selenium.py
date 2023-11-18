import time
from functools import lru_cache

from pydantic import HttpUrl
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By

from autobots.core.logging.log import Log
from autobots.core.settings import SettingsProvider, Settings


class Selenium:

    def __init__(self, options: Options = Options()):
        # Do not open browser
        # options.add_argument("--no-sandbox")
        options.add_argument("--headless")
        options.add_argument("--setDefaultBrowser")
        options.add_argument("--disable-pinch")

        # Expensive operation!! so do it once and close resource at the end
        self.driver = webdriver.Firefox(options=options, service=FirefoxService(GeckoDriverManager().install()))

    async def read_url_text(self, url: HttpUrl, xpath: str = "/html/body") -> str:
        Log.bind(url=url).debug("Reading url")
        # Target URL
        self.driver.get(url.unicode_string())
        # To load entire webpage
        time.sleep(5)

        # whole body text
        text: str = self.driver.find_element(By.XPATH, xpath).text
        return text

    async def read_url(self, url: HttpUrl, ) -> str:
        Log.bind(url=url).debug("Reading url")
        # Target URL
        self.driver.get(url.unicode_string())
        # To load entire webpage
        time.sleep(5)

        # whole body text
        html: str = self.driver.page_source
        return html

    def __del__(self):
        # Closing the driver
        self.driver.close()
        self.driver.quit()


@lru_cache
def get_selenium(settings: Settings = SettingsProvider.sget()) -> Selenium:
    return Selenium()
