import logging
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from autobots.api.deps import get_db
from sqlalchemy.orm import Session
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from starlette.responses import RedirectResponse
from autobots.ads.google.db_operations import save_refresh_token
import requests
from autobots.core.settings import get_settings
from .....ads.google.google_utils import get_account_hierarchy, user_has_ad_manager_account

logger = logging.getLogger(__name__)


# Google OAuth 2.0 constants from environment
CLIENT_ID = get_settings().GOOGLE_CLIENT_ID
CLIENT_SECRET = get_settings().GOOGLE_CLIENT_SECRET
REDIRECT_URI = get_settings().GOOGLE_REDIRECT_URI

SCOPES = [
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
    'https://www.googleapis.com/auth/admanager',
    'https://www.googleapis.com/auth/adwords',
    'openid'
]

router = APIRouter()

@router.get("/start-auth/")
async def start_google_auth(request: Request, db: Session = Depends(get_db)):
    try:
        logger.info("Initiating Google OAuth flow for user.")

        # Create the flow using the client secrets file
        flow = Flow.from_client_config(
            {
                "installed": {
                    "client_id": CLIENT_ID,
                    "client_secret": CLIENT_SECRET,
                    "redirect_uris": [REDIRECT_URI],
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                }
            },
            scopes=SCOPES,
        )

        # Set the redirect URI (this is required for the next step)
        flow.redirect_uri = REDIRECT_URI

        # Generate the authorization URL
        authorization_url, _ = flow.authorization_url(
            access_type="offline",  # This ensures a refresh token is returned
            prompt="consent",       # This ensures the user is prompted every time
            include_granted_scopes="true"
        )

        # Redirect the user to the generated authorization URL
        return RedirectResponse(authorization_url)

    except Exception as e:
        
        logger.error(f"Error during Google OAuth initialization: {str(e)}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while starting the Google auth process."
        )

@router.get("/oauth2callback/")
async def google_auth_callback(request: Request, db: Session = Depends(get_db)):
    try:

        logger.info("Fetching access and refresh tokens from Google.")

        # Extract authorization code
        code = request.query_params.get("code")       
        
        if not code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Authorization code is missing."
            )

        # Create the flow using the client secrets and then provide the code
        flow = Flow.from_client_config(
            {
                "installed": {
                    "client_id": CLIENT_ID,
                    "client_secret": CLIENT_SECRET,
                    "redirect_uris": [REDIRECT_URI],
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                }
            },
            scopes=SCOPES,
        )
        flow.redirect_uri = REDIRECT_URI

        
        # Use the authorization code to get the access and refresh tokens
        flow.fetch_token(code=code)

        # Extract the access token
        access_token = flow.credentials.token

        if not user_has_ad_manager_account(access_token):
            raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not have an Ad Manager account."
        )

        # Get user's email using the access token
        response = requests.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        response.raise_for_status()  # Raise an exception for HTTP errors
        user_info = response.json()
        user_email = user_info["email"]
        print(f"User email: {user_email}")

        # Save the refresh token to your database
        refresh_token = flow.credentials.refresh_token
        print(f"Refresh token: {refresh_token}")

    # Fetch the account hierarchy
        account_hierarchy = get_account_hierarchy(access_token)

        # Extract manager accounts and individual ad accounts from the hierarchy        
        for account in account_hierarchy:
            manager_account_id = account.get("id")
            manager_account_name = account.get("descriptive_name")

            # Check if there are individual accounts for this manager
            if account.get("manager"):
                for individual_account in account.get("individual_accounts", []):
                    individual_account_id = individual_account.get("id")
                    individual_account_name = individual_account.get("descriptive_name")

                    # Save to database for each individual account
                    save_refresh_token(user_email, refresh_token, manager_account_id, manager_account_name, individual_account_id, individual_account_name)
            else:
                # This is an individual account without an explicit manager in the current hierarchy
                save_refresh_token(user_email, refresh_token, manager_account_id, manager_account_name, manager_account_id, manager_account_name)

    except Exception as e:
        logger.error(f"Error during google auth redirect : {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error fetching tokens from Google or retrieving user's email."
        )
    # This is for testing purpose. This needs to be replaced with actual end point from where the auth is initiated.    
    return RedirectResponse(url=f"/static/google/index.html?email={user_email}")