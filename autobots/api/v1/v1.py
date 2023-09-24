from fastapi import APIRouter
from autobots.api.v1.ads.google import google_auth, ad_campaigns, google_ads
from autobots.api.v1 import api_hello, api_auth, api_prompts, api_graphs, api_actions, api_action_graphs, api_docs, \
    api_datastore
from autobots.core.settings import get_settings
from autobots.api.v1.ads.google import google_accounts, google_ad_groups


router = APIRouter(prefix=get_settings().API_v1)
router.include_router(api_hello.router, prefix=get_settings().API_Hello, tags=["hello"])
router.include_router(api_auth.router, prefix=get_settings().API_AUTH, tags=["auth"])
router.include_router(api_actions.router, prefix=get_settings().API_ACTIONS, tags=["actions"])
router.include_router(api_action_graphs.router, prefix=get_settings().API_ACTION_GRAPHS, tags=["action_graphs"])
router.include_router(api_datastore.router, prefix=get_settings().API_DATASTORE, tags=["datastore"])
router.include_router(api_prompts.router, prefix=get_settings().API_PROMPTS, tags=["prompts"])
# router.include_router(api_graphs.router, prefix=get_settings().API_GRAPHS, tags=["graphs"])
#router.include_router(google_auth.router, prefix=get_settings().GOOGLE_ADS_AUTH, tags=["google_ads"])
router.include_router(ad_campaigns.router, prefix=get_settings().GOOGLE_ADS_CAMPAIGNS, tags=["google_ads_campaigns"])
router.include_router(google_accounts.router, prefix=get_settings().GOOGLE_ADS_ACCOUNTS, tags=["google_ads_accounts"])
router.include_router(google_ad_groups.router, prefix=get_settings().GOOGLE_ADS_GROUPS, tags=["google_ads_groups"])
router.include_router(google_ads.router, prefix=get_settings().GOOGLE_ADS, tags=["google_ads"])



router_docs = APIRouter(prefix=get_settings().API_v1)
router.include_router(api_docs.router, prefix="", tags=["docs"])
