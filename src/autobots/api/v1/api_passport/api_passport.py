from fastapi import APIRouter, Depends, HTTPException
from src.autobots.passport.passport import Passport
from src.autobots.passport.passport_doc_model import APIKeyCreate
from src.autobots.passport.passport_crud import APIKeyCRUD

router = APIRouter(prefix="/api/poll_graph", tags=["poll_graph"])

@router.post("/register", response_model=APIKeyCreate)
async def register_api_key(
    api_key_create: APIKeyCreate,
    passport: Passport = Depends(Passport)
):
    return await passport.register_api_key(api_key_create)

@router.put("/update", response_model=APIKeyCreate)
async def update_api_key(
    api_key_create: APIKeyCreate,
    passport: Passport = Depends(Passport)
):
    return await passport.update_api_key(api_key_create)
