import time
from functools import lru_cache

from pydantic import HttpUrl
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By

from autobots.core.logging.log import Log


class Selenium:

    def __init__(self, options: Options = Options()):
        # Do not open browser
        # options.add_argument("--no-sandbox")
        options.add_argument("--headless")
        # options.add_argument("--setDefaultBrowser")
        options.add_argument("--disable-pinch")

        self.browser_options = options
        self.browser_service = FirefoxService(GeckoDriverManager().install())
        # Expensive operation!! so do it once and close resource at the end
        # self.driver = webdriver.Firefox(options=options, service=self.browser_service)

    def get_webdriver(self):
        driver = webdriver.Firefox(options=self.browser_options, service=self.browser_service)
        return driver

    async def read_url_text(self, url: HttpUrl, xpath: str = "/html/body") -> str:
        with self.get_webdriver() as driver:
            Log.bind(url=url).debug("Reading url")
            # Target URL
            driver.get(url.unicode_string())
            # To load entire webpage
            time.sleep(5)

            # whole body text
            text: str = self.driver.find_element(By.XPATH, xpath).text
            return text

    async def read_url_v1(self, url: HttpUrl, xpath: str = "/html/body", attribute: str = "") -> str:
        with self.get_webdriver() as driver:
            Log.bind(url=url).debug("Reading url")
            # Target URL
            driver.get(url.unicode_string())
            # To load entire webpage
            time.sleep(5)

            resp = ""
            if xpath and attribute:
                resp = driver.find_element(By.XPATH, xpath).get_attribute(attribute)
            elif xpath and not attribute:
                resp = driver.find_element(By.XPATH, xpath).text
            else:
                resp: str = driver.page_source

            return resp

    async def read_url(self, url: HttpUrl, ) -> str:
        with self.get_webdriver() as driver:
            Log.bind(url=url).debug("Reading url")
            # Target URL
            driver.get(url.unicode_string())
            # To load entire webpage
            time.sleep(5)

            # whole body text
            html: str = driver.page_source
            return html

    def __del__(self):
        # Closing the driver
        # self.driver.close()
        # self.driver.quit()
        pass


@lru_cache
def get_selenium() -> Selenium:
    return Selenium()
