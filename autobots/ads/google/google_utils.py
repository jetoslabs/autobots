import datetime
from typing import List
import requests
import logging
from fastapi import Depends, HTTPException, status
from google.oauth2.credentials import Credentials
import google.ads.googleads.client
from google.ads.googleads.errors import GoogleAdsException
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials as GoogleCredentials
from autobots.ads.google.google_ads_campaigns import CampaignCreate, AdGroupCreate, AdCreate, AdvertisingChannelType, ManualCPC, MaximizeConversionValue, MaximizeConversions, ResponsiveSearchAdCreate, TargetCPA, TargetROAS
from autobots.core.settings import get_settings
from google.auth.credentials import AnonymousCredentials
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException  


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Google OAuth 2.0 constants
CLIENT_ID = get_settings().GOOGLE_CLIENT_ID
CLIENT_SECRET = get_settings().GOOGLE_CLIENT_SECRET
DEVELOPER_TOKEN = get_settings().DEVELOPER_TOKEN
ENVIRONMENT = get_settings().ENVIRONMENT

# Google Ads API constants
TEST_MANAGER_ACCOUNT_ID = get_settings().TEST_MANAGER_ACCOUNT_ID



def get_google_ads_client(access_token: str):
    """Return a GoogleAdsClient instance authenticated with the provided access token."""
    return GoogleAdsClient(credentials=Credentials(access_token), developer_token=DEVELOPER_TOKEN)


def get_access_token_from_refresh_token(refresh_token):
    logger.info("Attempting to get access token using refresh token.")
    token_endpoint = "https://oauth2.googleapis.com/token"
    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }
    response = requests.post(token_endpoint, data=payload)
    token_response = response.json()

    if "access_token" in token_response:
        logger.info("Successfully obtained access token.")
        return token_response["access_token"]
    else:
        error = token_response.get("error", "")
        error_description = token_response.get("error_description", "")
        logger.error(f"Error fetching access token: {error} - {error_description}")

        if error == "invalid_grant":
            logger.warning("Refresh token is invalid. User reauthorization required.")            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session expired."
            )
        else:
            raise Exception(f"Failed to obtain access token. Error: {error} - {error_description}")
    
def user_has_ad_manager_account(access_token: str) -> bool:
    """
    Checks if the user associated with the provided access token has any Ad Manager accounts.

    Args:
        access_token (str): The access token for the user's session.

    Returns:
        bool: True if the user has an Ad Manager account, False otherwise.
    """
    logger.info("Checking if user has an Ad Manager account.")

    client = get_google_ads_client(access_token)
    customer_service = client.get_service("CustomerService")

    try:
        # Fetch the list of accessible customers
        accessible_customers = customer_service.list_accessible_customers()
        return bool(accessible_customers.resource_names)
        
    except GoogleAdsException as e:
        for error in e.failure.errors:
            logger.error(f"Error with message: {error.message}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error checking for Ad Manager account: {e}"
        )
    except Exception as e:
        logger.error(f"Unexpected error checking for Ad Manager account: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error checking for Ad Manager account: {e}"
        )

def create_google_ad_campaign(access_token, campaign_details: CampaignCreate):

    ad_manager_account = campaign_details.ad_manager_account_id
    ad_account = str(campaign_details.ad_account_id)

    logger.info(f"Attempting to create Google ad campaign for customer ID: {ad_manager_account} and ad account ID: {ad_account}")
    
    # Use the abstracted client creation logic
    client = get_google_ads_client(access_token)

    client.login_customer_id = str(ad_manager_account)

    # Get the service client for campaigns
    campaign_service = client.get_service("CampaignService")

    # Construct campaign operation
    campaign_operation = client.get_type("CampaignOperation")
    campaign = campaign_operation.create
    campaign.name = campaign_details.name
    campaign.status = client.enums.CampaignStatusEnum.PAUSED # Set the campaign status to PAUSED by default


    # For the advertising_channel_type
    channel_type_enum = client.enums.AdvertisingChannelTypeEnum
    channel_type_value = getattr(channel_type_enum, campaign_details.advertising_channel_type.name, None)
    if channel_type_value:
        campaign.advertising_channel_type = channel_type_value
    else:
        raise ValueError(f"Invalid advertising channel type: {campaign_details.advertising_channel_type.name}")

    # Set budget details
    budget = client.get_type("CampaignBudget")
    budget.name = f"Budget {campaign_details.name} {datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"

    budget.amount_micros = int(campaign_details.budget * 1e6)  # Budget is in dollars, but API expects it in micros

    # For the budget delivery method, if it's provided
    if campaign_details.budget_delivery_method:
        delivery_method_enum = client.enums.BudgetDeliveryMethodEnum
        delivery_method_value = getattr(delivery_method_enum, campaign_details.budget_delivery_method.name, None)
        if delivery_method_value:
            budget.delivery_method = delivery_method_value
        else:
            raise ValueError(f"Invalid budget delivery method: {campaign_details.budget_delivery_method.name}")
    
    # Get the service client for campaign budgets
    campaign_budget_service = client.get_service("CampaignBudgetService")

    # Create the campaign budget
    campaign_budget_operation = client.get_type("CampaignBudgetOperation")
    campaign_budget_operation.create.CopyFrom(budget)
    budget_response = campaign_budget_service.mutate_campaign_budgets(customer_id=ad_account, operations=[campaign_budget_operation])
    budget_resource_name = budget_response.results[0].resource_name
    campaign.campaign_budget = budget_resource_name

    client.copy_from(campaign.manual_cpc, client.get_type("ManualCpc"))

    try:
       # Send the campaign operation
        response = campaign_service.mutate_campaigns(customer_id=ad_account, operations=[campaign_operation])
        
        # Extract campaign ID from the resource name
        campaign_id = response.results[0].resource_name.split('/')[-1]
        
        # Construct the campaign URL
        campaign_url = f"https://ads.google.com/aw/campaigns?campaignId={campaign_id}"
        
        logger.info(f"Successfully created Google ad campaign. Resource Name: {response.results[0].resource_name}")
        logger.info(f"Campaign URL: {campaign_url}")  # Logging the campaign URL
        
        # Extract and return the campaign resource name from the response
        return {"status": "success", "campaign_resource_name": response.results[0].resource_name, "campaign_url": campaign_url}
    
    
    except GoogleAdsException as ex:
        logger.error(f"Google Ads API error while creating campaign: {ex.failure.errors}")
        return {"status": "error", "errors": ex.failure.errors}
    
    except Exception as e:
        logger.error(f"Error while creating campaign: {str(e)}")
        return {"status": "error", "message": str(e)}


def fetch_google_ad_accounts(customer_id: str, access_token: str) -> list:
    """Fetch the list of ad accounts from Google Ad Manager."""
    logger.info(f"Fetching ad accounts for customer_id: {customer_id}")

    # Set up the client using the specific access token
    client = get_google_ads_client(access_token)  # Pass the access_token to the utility function

    # Set up the GoogleAdsService client
    google_ads_service = client.get_service("GoogleAdsService")
    
    # Define the query to fetch ad accountsl
    query = """
        SELECT customer.id, customer.descriptive_name, customer.test_account
        FROM customer_client
        WHERE customer_client.client_customer != NULL
    """
    
    ad_accounts = []
    
    try:
        # Execute the search request
        response = google_ads_service.search(customer_id=customer_id, query=query)
        for row in response:
            ad_accounts.append({
                "id": row.customer.id.value,
                "name": row.customer.descriptive_name.value,
                "test_account": row.customer.test_account.value
            })
        logger.info(f"Successfully fetched {len(ad_accounts)} ad accounts for customer_id: {customer_id}")
    except GoogleAdsException as ex:
        logger.error(f"GoogleAdsException encountered while fetching ad accounts for customer_id {customer_id}. Error: {ex.error_code}")        
    except Exception as e:
        logger.error(f"Unexpected error occurred while fetching ad accounts for customer_id {customer_id}. Error: {str(e)}")        
    
    return ad_accounts


def get_account_hierarchy(auth_token: str) -> list:
    """Fetches the account hierarchy from Google Ad Manager."""
    logger.info(f"Fetching account hierarchy using provided auth token")

    # Set up the client using the specific auth token
    client = get_google_ads_client(auth_token)

    # Gets instances of the GoogleAdsService and CustomerService clients.
    googleads_service = client.get_service("GoogleAdsService")
    customer_service = client.get_service("CustomerService")

    # Query to fetch all child accounts without level restriction
    query = """
        SELECT 
          customer_client.client_customer, 
          customer_client.level, 
          customer_client.manager, 
          customer_client.descriptive_name, 
          customer_client.currency_code, 
          customer_client.time_zone, 
          customer_client.id,
          customer.test_account
        FROM customer_client
    """

    hierarchy_data = []
    manager_data = {}
    
    # Recursive function to fetch hierarchy
    def fetch_hierarchy(customer_id: str):
        response = googleads_service.search(customer_id=customer_id, query=query)
        for googleads_row in response:
            customer_client = googleads_row.customer_client

            # If manager
            if customer_client.level == 0:
                manager_data = {
                    "client_customer": customer_client.client_customer,
                    "level": customer_client.level,
                    "manager": customer_client.manager,
                    "descriptive_name": customer_client.descriptive_name,
                    "currency_code": customer_client.currency_code,
                    "time_zone": customer_client.time_zone,
                    "id": customer_client.id,
                    "test_account": customer_client.test_account,
                    "individual_accounts": []
                }
                hierarchy_data.append(manager_data)

            # If individual account
            elif customer_client.level == 1:
                individual_account_data = {
                    "client_customer": customer_client.client_customer,
                    "level": customer_client.level,
                    "manager": customer_client.manager,
                    "descriptive_name": customer_client.descriptive_name,
                    "currency_code": customer_client.currency_code,
                    "time_zone": customer_client.time_zone,
                    "id": customer_client.id,
                    "test_account": customer_client.test_account
                }
                manager_data["individual_accounts"].append(individual_account_data)

    customer_resource_names = customer_service.list_accessible_customers().resource_names
    
    for resource_name in customer_resource_names:
        customer_id = googleads_service.parse_customer_path(resource_name)["customer_id"]
        
        if ENVIRONMENT == "DEVELOPMENT":
            if resource_name == TEST_MANAGER_ACCOUNT_ID:
                fetch_hierarchy(customer_id)
                break
        else:
            fetch_hierarchy(customer_id)

    return hierarchy_data


def fetch_google_ad_campaigns(access_token: str, manager_accounts: List[dict]) -> List[dict]:
    """Fetch all Google ad campaigns for the given manager accounts and their associated individual ad accounts."""
    
    # Use the abstracted client creation logic
    client = get_google_ads_client(access_token)
    
    
    
    # Define a GAQL query to fetch all campaigns
    query = """
        SELECT 
          campaign.id, 
          campaign.name, 
          campaign.status, 
          campaign.advertising_channel_type,
          campaign.start_date,
          campaign.end_date
        FROM campaign
    """
    
    campaigns = []
    
    # Iterate over all manager accounts
    for manager in manager_accounts:
        # If accessing a client customer, set the manager's customer ID in the login-customer-id header
        client.login_customer_id = str(manager["id"])

        # Get the service client for campaigns
        googleads_service = client.get_service("GoogleAdsService")

        
    
        # For each individual ad account under this manager, fetch campaigns
        for individual_account in manager.get("individual_accounts", []):
            # Query campaigns for the individual account
            response = googleads_service.search(customer_id=str(individual_account["id"]), query=query)
            
            for row in response:
                campaigns.append({
                    "manager_id": manager["id"],
                    "individual_account_id": individual_account["id"],
                    "id": row.campaign.id,
                    "name": row.campaign.name,
                    "status": row.campaign.status,
                    "advertising_channel_type": row.campaign.advertising_channel_type,
                    "start_date": row.campaign.start_date,
                    "end_date": row.campaign.end_date
                })
    
    return campaigns

def create_ad_group(access_token: str, ad_group_details: AdGroupCreate):
    """Create an ad group under a given campaign."""

    # Use the abstracted client creation logic
    client = get_google_ads_client(access_token)
    client.login_customer_id = str(ad_group_details.ad_manager_account_id)

    # Get the service client for ad groups
    ad_group_service = client.get_service("AdGroupService")

    # Get the service client for campaigns to access utility methods
    campaign_service = client.get_service("CampaignService")

    # Construct ad group operation
    ad_group_operation = client.get_type("AdGroupOperation")

    # Set the ad group attributes
    ad_group = ad_group_operation.create
    ad_group.name = ad_group_details.name
    ad_group.campaign = campaign_service.campaign_path(str(ad_group_details.ad_account_id), ad_group_details.campaign_id)
    ad_group.status = getattr(client.enums.AdGroupStatusEnum, ad_group_details.status.name)
    ad_group.type_ = client.enums.AdGroupTypeEnum.SEARCH_STANDARD
    ad_group.cpc_bid_micros = int(ad_group_details.bid_amount * 1e6)  # Convert bid amount to micros

    try:
        # Send the ad group operation
        response = ad_group_service.mutate_ad_groups(customer_id=str(ad_group_details.ad_account_id), operations=[ad_group_operation])

        ad_group_id = response.results[0].resource_name.split('/')[-1]
        campaign_id = ad_group_details.campaign_id
        
        ad_group_url = f"https://ads.google.com/aw/keywords?campaignId={campaign_id}&adGroupId={ad_group_id}"

        return {
            "status": "success",
            "ad_group_resource_name": response.results[0].resource_name,
            "ad_group_url": ad_group_url
        }
    except GoogleAdsException as ex:
        return {"status": "error", "errors": ex.failure.errors}
    

def fetch_ad_groups(access_token: str, manager_accounts: List[dict]) -> List[dict]:
    """Fetch all ad groups for the given manager accounts and their associated individual ad accounts."""
    
    # Use the abstracted client creation logic
    client = get_google_ads_client(access_token)
    
    # Define a GAQL query to fetch all ad groups
    query = """
        SELECT 
          ad_group.id, 
          ad_group.name, 
          ad_group.status,
          ad_group.campaign
        FROM ad_group
    """
    
    ad_groups = []
    
    # Iterate over all manager accounts
    for manager in manager_accounts:
        # Set the manager's customer ID in the login-customer-id header
        client.login_customer_id = str(manager["id"])
        
        # Get the service client for ad groups
        googleads_service = client.get_service("GoogleAdsService")

        # For each individual ad account under this manager, fetch ad groups
        for individual_account in manager.get("individual_accounts", []):
            # Query ad groups for the individual account
            response = googleads_service.search(customer_id=str(individual_account["id"]), query=query)
            
            for row in response:
                ad_groups.append({
                    "manager_id": manager["id"],
                    "individual_account_id": individual_account["id"],
                    "id": row.ad_group.id,
                    "name": row.ad_group.name,
                    "status": row.ad_group.status,
                    "campaign": row.ad_group.campaign
                })
    
    return ad_groups

def create_responsive_ad(access_token: str, rsa_details: ResponsiveSearchAdCreate) -> dict:
    """Utility function to create a responsive search ad."""
    
    client = get_google_ads_client(access_token)
    
    # Set the login_customer_id
    client.login_customer_id = str(rsa_details.ad_manager_account_id)
    
    # Get the ad_group_path for the given ad_account_id and ad_group_id
    ad_group_service = client.get_service("AdGroupService")
    ad_group_path = ad_group_service.ad_group_path(rsa_details.ad_account_id, rsa_details.ad_group_id)
    
    # Construct RSA
    ad = client.get_type("Ad")
    ad.final_urls.append(rsa_details.final_url)
    rsa = ad.responsive_search_ad
    
    # Add headlines and descriptions to the RSA
    for headline in rsa_details.headlines:
        text_asset = client.get_type("AdTextAsset")
        text_asset.text = headline
        rsa.headlines.append(text_asset)
    for description in rsa_details.descriptions:
        text_asset = client.get_type("AdTextAsset")
        text_asset.text = description
        rsa.descriptions.append(text_asset)
    
    # Create AdGroupAd
    ad_group_ad = client.get_type("AdGroupAd")
    ad_group_ad.ad_group = ad_group_path
    ad_group_ad.ad.CopyFrom(ad)
    
    # Use AdGroupAdService to create the RSA
    ad_group_ad_service = client.get_service("AdGroupAdService")
    ad_group_ad_operation = client.get_type("AdGroupAdOperation")
    ad_group_ad_operation.create.CopyFrom(ad_group_ad)
    
    response = ad_group_ad_service.mutate_ad_group_ads(customer_id=str(rsa_details.ad_account_id), operations=[ad_group_ad_operation])
    
    resource_components = response.results[0].resource_name.split('/')
    ad_account_id = resource_components[1]
    ad_group_id_and_ad_id = resource_components[3].split('~')
    ad_group_id = ad_group_id_and_ad_id[0]
    ad_id = ad_group_id_and_ad_id[1]
    
    #TODO: The following URL doesnot work. Need to find a straight forward way to get the URL instead of genearting this URL.
    ad_url = f"https://ads.google.com/aw/ads/assetdetails?ocid={ad_account_id}&workspaceId=0&ascid={ad_account_id}&adId={ad_id}&adGroupIdForAd={ad_group_id}"

    return {
    "status": "success",
    "ad_resource_name": response.results[0].resource_name,
    "ad_url": ad_url
    }

def fetch_ads(access_token: str, manager_accounts: List[dict]) -> List[dict]:
    """Fetch all ads across all ad groups, campaigns, and accounts."""

    # Use the abstracted client creation logic
    client = get_google_ads_client(access_token)
    ads = []
    
    # Loop through Ad Manager accounts
    for manager in manager_accounts:
        manager_id = manager["id"]
        client.login_customer_id = str(manager_id)
        googleads_service = client.get_service("GoogleAdsService")
        
        # Loop through individual accounts
        for individual_account in manager.get("individual_accounts", []):
            account_id = individual_account["id"]
            
            # Fetch campaigns for the individual account
            campaign_query = """
                SELECT campaign.id FROM campaign
            """
            campaigns = googleads_service.search(customer_id=str(account_id), query=campaign_query)
            
            for campaign_row in campaigns:
                # Fetch ad groups for the campaign
                ad_group_query = f"""
                    SELECT ad_group.id FROM ad_group WHERE ad_group.campaign = '{campaign_row.campaign.resource_name}'
                """
                ad_groups = googleads_service.search(customer_id=str(account_id), query=ad_group_query)
                
                for ad_group_row in ad_groups:
                    ad_group_id = ad_group_row.ad_group.id
                    # Fetch ads for the ad group
                    ad_query = f"""
                        SELECT 
                            ad_group_ad.ad.id,
                            ad_group_ad.ad.final_urls,
                            ad_group_ad.ad.responsive_search_ad.headlines,
                            ad_group_ad.ad.responsive_search_ad.descriptions
                        FROM ad_group_ad
                        WHERE 
                            ad_group_ad.ad.type = 'RESPONSIVE_SEARCH_AD'
                            AND ad_group_ad.ad_group = '{ad_group_row.ad_group.resource_name}'
                    """
                    ad_results = googleads_service.search(customer_id=str(account_id), query=ad_query)
                    
                    for ad_row in ad_results:
                        ad = ad_row.ad_group_ad.ad
                        final_urls = ad.final_urls
                        # Convert RepeatedScalarContainer to a list
                        if isinstance(final_urls, google._upb._message.RepeatedScalarContainer):
                            final_urls = list(final_urls)

                        ads.append({
                            "manager_id": manager_id,
                            "account_id": account_id,
                            "ad_group_id": ad_group_id,
                            "ad_id": ad.id,
                            "headlines": [asset.text for asset in ad.responsive_search_ad.headlines],
                            "descriptions": [description.text for description in ad.responsive_search_ad.descriptions],
                            "final_urls": final_urls
                        })

    return ads
