import asyncio
from typing import List, Dict
from loguru import logger
import requests
from src.autobots.core.settings import Settings, SettingsProvider
settings = SettingsProvider.sget()

scraping_url ="https://api.scrapingdog.com/linkedin"

def get_linkedin_scrape(linkedin_id):
    params= {"api_key": settings.SCRAPING_API_KEY,"type":"profile" ,"linkId":linkedin_id}
    response= requests.get(scraping_url, params=params)
    return response.json()
