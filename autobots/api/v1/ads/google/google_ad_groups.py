import logging
from typing import List
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import EmailStr
from autobots.ads.google.db_operations import get_refresh_token

from autobots.ads.google.google_ads_campaigns import AdGroupCreate
from autobots.ads.google.google_utils import create_ad_group, fetch_ad_groups, get_access_token_from_refresh_token

router = APIRouter()

logger = logging.getLogger(__name__)

@router.post("/ad-group/")
async def create_adgroup(email: EmailStr, ad_group_details: AdGroupCreate):
    """Create an ad group on behalf of the user using the Google Ad Manager API."""
    
    if not email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email is required.")
    
    # Retrieve the stored refresh token for the user
    token_data = get_refresh_token(email)
    if not token_data or not token_data.get("refresh_token"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token not found for the user.")
    
    # Validate the Ad Manager account and Ad account IDs
    google_ads_data = token_data.get("google_ads", {})
    manager_accounts = google_ads_data.get("manager_accounts", [])
    
    target_manager = None
    for manager in manager_accounts:
        if manager.get("id") == ad_group_details.ad_manager_account_id:
            target_manager = manager
            break
    
    if not target_manager:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Provided Ad Manager account ID doesn't match with the stored data.")
    
    individual_accounts = target_manager.get("individual_accounts", [])
    if not any(acc["id"] == ad_group_details.ad_account_id for acc in individual_accounts):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Provided Ad account ID doesn't match with the stored data under the given Ad Manager account.")
    
    # Generate a new access token using the stored refresh token
    try:
        access_token = get_access_token_from_refresh_token(token_data["refresh_token"])
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Failed to obtain access token.")
    
    # Use the access token to create an ad group
    try:
        ad_group_response = create_ad_group(access_token, ad_group_details)
        return ad_group_response
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create ad group.")
    

@router.get("/ad-groups/")
async def list_ad_groups(email: EmailStr) -> List[dict]:
    """Retrieve the list of ad groups for the specified user."""
    
    if not email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email is required.")
    
    # Retrieve the stored refresh token for the user
    token_data = get_refresh_token(email)
    if not token_data or not token_data.get("refresh_token"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token not found for the user.")
    
    # Generate a new access token using the stored refresh token
    try:
        access_token = get_access_token_from_refresh_token(token_data["refresh_token"])
    except Exception as e:
        logger.error(f"Failed to generate access token for email {email}. Error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Failed to obtain access token.")
    
    # Fetch ad groups
    try:
        ad_groups = fetch_ad_groups(access_token, token_data["google_ads"]["manager_accounts"])
        return ad_groups
    except Exception as e:
        logger.error(f"Failed to fetch ad groups for email {email}. Error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch ad groups.")