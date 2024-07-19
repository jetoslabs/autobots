import asyncio
from typing import List, Dict
from loguru import logger
import requests

scraping_url ="https://api.scrapingdog.com/linkedin"
params= {"api_key": "","type":"profile" ,"linkId":"kefalu"}
response= requests.get(scraping_url, params=params)
print( response.json())



# kaspr_url = "https://api.developers.kaspr.io/profile/linkedin"
# response= requests.get(kaspr_url, params=params)
# print( response.json())

# import requests
# import json


# apiEndPoint = "http://api.scraping-bot.io/scrape/data-scraper"

# payload = json.dumps({
#   "scraper": "linkedinCompanyProfile",
#   "url": "https://www.linkedin.com/in/khushal-sethi-436109151/"
# })
# headers = {
#   'Content-Type': "application/json"
# }

# response = requests.request("POST", apiEndPoint, data=payload, auth=(username,apiKey), headers=headers)
# print(response)
