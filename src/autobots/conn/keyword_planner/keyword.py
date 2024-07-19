from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
path = "/Users/khushalsethi/godelsales/autobots/google.yaml"
# Load the configuration from google-ads.yaml
client = GoogleAdsClient.load_from_storage(path)

# Get the GoogleAdsService client
keyword_plan_idea_service = client.get_service("KeywordPlanIdeaService")

# Create the request
request = {
    'customer_id': '7574633676',
    'language': 'en',
    'geo_target_constants': ['geoTargetConstantId'],
    'keyword_plan_network': 'GOOGLE_SEARCH',
    'keyword_seed': {
        'keywords': ['keyword1', 'keyword2']
    }
}

response = keyword_plan_idea_service.generate_keyword_ideas(request=request)

for result in response.results:
    print(f'Keyword: {result.text}')
