import os
from typing import Dict, Any
from datetime import timedelta
from dotenv import load_dotenv

from bcrypt import checkpw

from app.repository.account_repository import AccountRepository
from app.schemas.auth_schemas import SigninSchema

from app.lib.token_jwt import signin_access_token
from app.core.exceptions import InvalidCredentialsError

load_dotenv()


class SigninService:

    '''Service class to handle user sign-in operations.'''

    def __init__(self, account_repository: AccountRepository):
        self.account_repository = account_repository

    async def auth_service(self, data: SigninSchema) -> Dict[str, Any]:
        """API Authentication service"""
        user = await self.account_repository.get_account_by_email(data.email)
        if not user:
            raise InvalidCredentialsError()

        is_valid_password = checkpw(
            password=data.password.encode("utf-8"),
            hashed_password=user.password,
        )
        if not is_valid_password:
            raise InvalidCredentialsError()

        access_token = await signin_access_token(user_id=user.id)
        refresh_token = await signin_access_token(
            user_id=user.id,
            token_duration=timedelta(days=int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS")))
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
        }
