from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from motor.motor_asyncio import AsyncIOMotorDatabase
from src.autobots.core.database.mongo_base import get_mongo_db
from src.autobots.core.database.mongo_base_crud import CRUDBase
from src.autobots.passport.passport_doc_model import APIKeyDoc, APIKeyCreate, APIKeyFind
from src.autobots.passport.passport_crud import APIKeyCRUD

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class Passport:
    def __init__(self, db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
        self.api_key_crud = APIKeyCRUD(db)

    async def authenticate_user(self, token: str = Depends(oauth2_scheme)):
        try:
            api_key = await self.api_key_crud.find_one(APIKeyFind(token=token))
            if not api_key:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
            return api_key
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    async def register_api_key(self, api_key_create: APIKeyCreate):
        try:
            api_key = await self.api_key_crud.insert_one(api_key_create)
            return api_key
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    async def update_api_key(self, token: str, api_key_update: APIKeyCreate):
        try:
            existing_api_key = await self.api_key_crud.find_one(APIKeyFind(token=token))
            if not existing_api_key:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="API key not found")
            updated_api_key = await self.api_key_crud.update_one(api_key_update)
            return updated_api_key
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
