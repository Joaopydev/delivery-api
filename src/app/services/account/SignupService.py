import os
from typing import Dict, Any
from datetime import timedelta
from dotenv import load_dotenv

from bcrypt import hashpw, gensalt
from fastapi import HTTPException, status

from app.repository.account_repository import AccountRepository
from app.db.models.schemas import User
from app.schemas.auth_schemas import SignupSchema

from app.lib.token_jwt import signin_access_token

load_dotenv()


class SignupService:
    
    '''Service class to handle user sign-up operations.'''

    def __init__(self, account_repository: AccountRepository):
        self.account_repository = account_repository

    async def account_creation_service(self, data: SignupSchema) -> Dict[str, Any]:
        user = await self.account_repository.get_account_by_email(data.email)
        if user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already exists"
            )
        
        hashed_password = hashpw(
            password=data.password.encode("utf-8"),
            salt=gensalt(8)
        )
        new_user = await self.account_repository.create_account(data, hashed_password)

        access_token = await signin_access_token(user_id=new_user.id)
        refresh_token = await signin_access_token(
            user_id=new_user.id,
            token_duration=timedelta(days=int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS")))
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
        }
