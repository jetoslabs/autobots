from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from src.autobots.core.settings import Settings, SettingsProvider
# Load the configuration from google-ads.yaml
def get_keywords(keywords_seed, settings: Settings = SettingsProvider.sget()):
    config = {
        'developer_token': settings.developer_token,
        'client_id': settings.client_id,
        'client_secret': settings.client_secret,
        'refresh_token': settings.refresh_token,
        'login_customer_id': settings.login_customer_id
    }
    client = GoogleAdsClient.load_from_dict(config)

    # Get the GoogleAdsService client
    keyword_plan_idea_service = client.get_service("KeywordPlanIdeaService")

    # Create the request
    request = {
        'customer_id': settings.customer_id,
        'language': 'en',
        'geo_target_constants': ['geoTargetConstantId'],
        'keyword_plan_network': 'GOOGLE_SEARCH',
        'keyword_seed': {
            'keywords': keywords_seed
        }
    }

    response = keyword_plan_idea_service.generate_keyword_ideas(request=request)

    for result in response.results:
        print(f'Keyword: {result.text}')
    return response.results
