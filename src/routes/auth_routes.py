from typing import Dict, Any, Union, Annotated
from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from ..schemas.auth_schemas import SigninSchema, SignupSchema
from ..services.account.SigninService import SigninService
from ..services.account.SignupService import SignupService
from ..lib.token_jwt import verify_token, signin_access_token

from ..db.connection import get_database


auth_router = APIRouter(prefix="/auth", tags=["auth"])

@auth_router.post("/signin", status_code=status.HTTP_200_OK)
async def signin(
    data: Annotated[SigninSchema, OAuth2PasswordRequestForm],
    session: AsyncSession = Depends(get_database),
) -> Dict[str, Any]:

    signin_service = SigninService(session=session)
    auth_tokens = await signin_service.auth_service(data=data)

    return auth_tokens


@auth_router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(
    data: SignupSchema,
    session: AsyncSession = Depends(get_database)
) -> Dict[str, Any]:
    
    signup_service = SignupService(session=session)
    auth_tokens = await signup_service.account_creation_service(data=data)

    return auth_tokens


@auth_router.post("/refresh")
async def use_refresh_token(user_id: str = Depends(verify_token)) -> Dict[str, Any]:
    
    new_access_token = await signin_access_token(user_id=user_id)

    return {
        "acces_token": new_access_token,
        "token_type": "Bearer",
        "user": user_id
    }