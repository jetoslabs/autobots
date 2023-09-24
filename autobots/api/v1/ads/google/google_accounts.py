from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from autobots.api.deps import get_db
from autobots.ads.google.db_operations import get_refresh_token
from autobots.ads.google.google_utils import get_access_token_from_refresh_token, fetch_google_ad_accounts, get_account_hierarchy
import logging
from pydantic import EmailStr

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/get-ad-accounts/")
async def get_ad_accounts(email: EmailStr, db: Session = Depends(get_db)):
    """Fetch all ad accounts for the user using the Google Ad Manager API."""
    try:
        # Step 1: Retrieve the stored refresh token and customer id for the user
        token_data = get_refresh_token(email)
        if not token_data or not token_data.get("refresh_token"):
            logger.error(f"Refresh token not found for email: {email}")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token not found for the user.")
            
        # Step 2: Generate a new access token using the stored refresh token
        access_token = get_access_token_from_refresh_token(token_data["refresh_token"])
        if not access_token:
            logger.error(f"Failed to get access token for email: {email}")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Failed to generate an access token.")
            
        # Step 3: Fetch the account hierarchy
        hierarchy = get_account_hierarchy(access_token)
        if not hierarchy:
            logger.error(f"Failed to fetch account hierarchy for email: {email}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Failed to fetch account hierarchy.")
            
        return hierarchy

    except Exception as e:
        logger.error(f"Unexpected error occurred for email {email}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred.")