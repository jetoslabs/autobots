from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from autobots.api.deps import get_db
from autobots.ads.google.db_operations import get_refresh_token
from autobots.ads.google.google_ads_campaigns import CampaignCreate
from .....ads.google.google_utils import fetch_google_ad_campaigns, get_access_token_from_refresh_token, create_google_ad_campaign
import logging
from pydantic import EmailStr
from typing import List

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/create/")
async def create_ad_campaign(email: EmailStr, campaign_details: CampaignCreate, db: Session = Depends(get_db)):
    """Create an ad campaign on behalf of the user using the Google Ad Manager API."""
    
    if not email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email is required.")
    
    # Step 1: Retrieve the stored refresh token for the user
    token_data = get_refresh_token(email)
    if not token_data or not token_data.get("refresh_token"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token not found for the user.")
    
    
    # Validate the Ad Manager account and Ad account IDs
    google_ads_data = token_data.get("google_ads", {})
    manager_accounts = google_ads_data.get("manager_accounts", [])
    
    target_manager = None
    for manager in manager_accounts:
        if manager.get("id") == campaign_details.ad_manager_account_id:
            target_manager = manager
            break
    
    if not target_manager:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Provided Ad Manager account ID doesn't match with the stored data.")
    
    individual_accounts = target_manager.get("individual_accounts", [])
    if not any(acc["id"] == campaign_details.ad_account_id for acc in individual_accounts):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Provided Ad account ID doesn't match with the stored data under the given Ad Manager account.")
    
    # Step 2: Generate a new access token using the stored refresh token
    try:
        access_token = get_access_token_from_refresh_token(token_data["refresh_token"])
    except Exception as e:
        logger.error(f"Failed to generate access token for email {email}. Error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Failed to obtain access token.")
    
    # Step 3: Use the access token to create an ad campaign
    try:
        campaign_response = create_google_ad_campaign(access_token, campaign_details)
        return campaign_response
    except Exception as e:
        logger.error(f"Failed to create ad campaign for email {email}. Error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create ad campaign.")

@router.get("/list_campaigns/")
async def list_ad_campaigns(email: EmailStr) -> List[dict]:
    """List all ad campaigns on behalf of the user using the Google Ad Manager API."""
    
    if not email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email is required.")
    
    # Step 1: Retrieve the stored refresh token for the user
    token_data = get_refresh_token(email)
    if not token_data or not token_data.get("refresh_token"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token not found for the user.")
    
    # Step 2: Generate a new access token using the stored refresh token
    try:
        access_token = get_access_token_from_refresh_token(token_data["refresh_token"])
    except Exception as e:
        logger.error(f"Failed to generate access token for email {email}. Error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Failed to obtain access token.")
    
    # Step 3: Use the access token to fetch the list of ad campaigns
    try:
        campaigns = fetch_google_ad_campaigns(access_token, token_data["google_ads"]["manager_accounts"])
        return campaigns
    except Exception as e:
        logger.error(f"Failed to fetch ad campaigns for email {email}. Error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch ad campaigns.")