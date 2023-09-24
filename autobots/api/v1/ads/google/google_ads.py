import logging
from typing import List
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import EmailStr
from autobots.ads.google.db_operations import get_refresh_token
from autobots.ads.google.google_ads_campaigns import ResponsiveSearchAdCreate
from autobots.ads.google.google_utils import create_responsive_ad, fetch_ad_groups, fetch_ads, get_access_token_from_refresh_token

router = APIRouter()

logger = logging.getLogger(__name__)


@router.post("/create-responsive-ad/")
async def create_responsive_search_ad(email: EmailStr, ad_details: ResponsiveSearchAdCreate) -> dict:
    """Create a responsive search ad."""
    try:
        if not email:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email is required.")
        
        logger.info("Creating a responsive search ad for email: %s", email)

        
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
        
        # Validate the Ad Manager account and Ad account IDs
        google_ads_data = token_data.get("google_ads", {})
        manager_accounts = google_ads_data.get("manager_accounts", [])
        
        target_manager = None
        for manager in manager_accounts:
            if manager.get("id") == ad_details.ad_manager_account_id:
                target_manager = manager
                break
        
        if not target_manager:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Provided Ad Manager account ID doesn't match with the stored data.")
        
        individual_accounts = target_manager.get("individual_accounts", [])
        if not any(acc["id"] == ad_details.ad_account_id for acc in individual_accounts):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Provided Ad account ID doesn't match with the stored data under the given Ad Manager account.")     
        
        
        # Validate the ad group ID
        fetched_ad_groups = fetch_ad_groups(access_token, [target_manager])
        if not any(ad_group["id"] == ad_details.ad_group_id for ad_group in fetched_ad_groups):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Provided Ad Group ID doesn't match with the stored data under the given Ad Manager account and Ad account.")   
        
        
        # Create the responsive search ad        
        ad_response = create_responsive_ad(access_token, ad_details)
        return ad_response
    except Exception as e:
        logger.error(f"Failed to create responsive search ad for email {email}. Error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create responsive search ad.")

@router.get("/list-ads/")
async def list_ads(email: EmailStr) -> List[dict]:
    """List all ads for the user."""
    
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
    
    # Fetch the ads
    try:
        ads = fetch_ads(access_token, token_data["google_ads"]["manager_accounts"])
        return ads
    except Exception as e:
        logger.error(f"Failed to fetch ads for email {email}. Error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch ads.")