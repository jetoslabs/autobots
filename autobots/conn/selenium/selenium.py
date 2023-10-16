import time
from functools import lru_cache

import chromedriver_autoinstaller
from pydantic import HttpUrl
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from autobots.core.settings import SettingsProvider, Settings


class Selenium:

    def __init__(self, options: Options = Options()):
        # chromedriver_autoinstaller library will install ChromeDriver and add it to PATH if it is not already there
        chromedriver_autoinstaller.install()

        # options = Options()
        # Do not open browser
        options.add_argument("--headless=new")
        # # Do open browser
        # options.add_argument("--headless=new")
        # options.add_argument("--window-size=1920,1200")

        # Expensive operation!! so do it once and close resource at the end
        # WebDriver Chrome
        self.driver = webdriver.Chrome(options=options)

    async def read_url_text(self, url: HttpUrl, xpath: str = "/html/body") -> str:
        # Target URL
        self.driver.get(url.unicode_string())
        # To load entire webpage
        time.sleep(5)

        # whole body text
        text: str = self.driver.find_element(By.XPATH, xpath).text
        return text

    async def read_url(self, url: HttpUrl, ) -> str:
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
