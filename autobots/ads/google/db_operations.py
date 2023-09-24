import logging
from datetime import datetime
from typing import Optional
from pymongo.errors import PyMongoError
from fastapi import HTTPException

from autobots.database.mongo_base import get_mongo_db, get_mongo_db_collection

# Set up basic logging configuration
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

db = next(get_mongo_db())
refresh_tokens_collection = get_mongo_db_collection(db, "RefreshTokens")

def save_refresh_token(email: str, refresh_token: str, manager_account_id: str, manager_account_name: str, individual_account_id: str, individual_account_name: str):
    # Check if user already exists in DB
    user_data = refresh_tokens_collection.find_one({"email": email})

    # Create the account structure
    individual_account_data = {
        "id": individual_account_id,
        "name": individual_account_name
    }

    if user_data:
        manager_accounts = user_data.get("google_ads", {}).get("manager_accounts", [])
        
        # Check if the manager account already exists
        manager_exists = False
        for manager in manager_accounts:
            if manager["id"] == manager_account_id:
                manager_exists = True
                # Check if individual account exists, if not, append
                individual_exists = False
                for ind_acc in manager.get("individual_accounts", []):
                    if ind_acc["id"] == individual_account_id:
                        ind_acc["name"] = individual_account_name  
                        individual_exists = True
                        break
                if not individual_exists:
                    manager["individual_accounts"].append(individual_account_data)
                break

        # If manager account doesn't exist, create and append
        if not manager_exists:
            manager_data = {
                "id": manager_account_id,
                "name": manager_account_name,
                "individual_accounts": [individual_account_data]
            }
            manager_accounts.append(manager_data)

        # Update user data in DB
        refresh_tokens_collection.update_one(
            {"email": email},
            {
                "$set": {
                    "google_ads.manager_accounts": manager_accounts,
                    "last_modified": datetime.utcnow()
                }
            }
        )
    else:
        # Insert new user data
        manager_data = {
            "id": manager_account_id,
            "name": manager_account_name,
            "individual_accounts": [individual_account_data]
        }
        refresh_tokens_collection.insert_one({
            "email": email,
            "refresh_token": refresh_token,
            "google_ads": {
                "manager_accounts": [manager_data]
            },
            "created_at": datetime.utcnow(),
            "last_modified": datetime.utcnow()
        })


def get_refresh_token(email: str, manager_account_id: Optional[str] = None, individual_account_id: Optional[str] = None) -> dict:
    """Retrieve the refresh token, and specific manager or individual ad accounts for the given email from MongoDB."""
    logger.debug(f"Attempting to fetch data for email: {email}")
    try:
        user_doc = refresh_tokens_collection.find_one({"email": email})
        if not user_doc:
            raise HTTPException(status_code=404, detail="User not found.")
        
        # If specific IDs are provided, filter out the corresponding data
        if manager_account_id:
            user_doc["google_ads"]["manager_accounts"] = [acc for acc in user_doc.get("google_ads", {}).get("manager_accounts", []) if acc["id"] == manager_account_id]
            if individual_account_id:
                for manager in user_doc["google_ads"]["manager_accounts"]:
                    manager["individual_accounts"] = [ind_acc for ind_acc in manager.get("individual_accounts", []) if ind_acc["id"] == individual_account_id]

        logger.debug(f"Successfully fetched data for email: {email}")
        return {
            "refresh_token": user_doc["refresh_token"],
            "google_ads": user_doc.get("google_ads", {})
        }
    except PyMongoError as e:
        logger.error(f"Database error occurred while fetching token for email {email}: {e}")
        raise HTTPException(status_code=500, detail="Database error occurred.") from e

    
def get_refresh_token(email: str) -> dict:
    """Retrieve the refresh token, manager accounts, and individual ad accounts for the given email from MongoDB."""
    logger.debug(f"Attempting to fetch data for email: {email}")
    try:
        user_doc = refresh_tokens_collection.find_one({"email": email})
        if not user_doc:
            raise HTTPException(status_code=404, detail="User not found.")
        logger.debug(f"Successfully fetched data for email: {email}")
        return {
            "refresh_token": user_doc["refresh_token"],
            "google_ads": user_doc.get("google_ads", {})
        }
    except PyMongoError as e:
        logger.error(f"Database error occurred while fetching token for email {email}: {e}")
        raise HTTPException(status_code=500, detail="Database error occurred.") from e

