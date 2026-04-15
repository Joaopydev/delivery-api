from typing import Dict, Any, Annotated
from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from app.schemas.auth_schemas import SigninSchema, SignupSchema
from app.services.account.signin import SigninService
from app.services.account.signup import SignupService
from app.lib.token_jwt import verify_token, signin_access_token

from app.dependencies.account_dependencies import (
    get_signin_service,
    get_signup_service,
)

auth_router = APIRouter(prefix="/auth", tags=["auth"])

@auth_router.post("/signin", status_code=status.HTTP_200_OK)
async def signin(
    data: Annotated[SigninSchema, OAuth2PasswordRequestForm],
    signin_service: SigninService = Depends(get_signin_service),
) -> Dict[str, Any]:

    return await signin_service.auth_service(data=data)

@auth_router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(
    data: SignupSchema,
    signup_service: SignupService = Depends(get_signup_service),
) -> Dict[str, Any]:

    return await signup_service.account_creation_service(data=data)

@auth_router.post("/refresh")
async def use_refresh_token(user_id: str = Depends(verify_token)) -> Dict[str, Any]:

    new_access_token = await signin_access_token(user_id=user_id)

    return {
        "acces_token": new_access_token,
        "token_type": "Bearer",
        "user": user_id
    }
