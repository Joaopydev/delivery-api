import os
from typing import Dict, Any, Optional
from datetime import timedelta
from dotenv import load_dotenv

from bcrypt import checkpw
from fastapi import HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ...db.models.schemas import User
from ...schemas.auth_schemas import SigninSchema

from ...lib.token_jwt import signin_access_token

load_dotenv()


class SigninService:

    def __init__(self, session: Optional[AsyncSession]):
        self.session = session

    async def auth_service(self, data: SigninSchema) -> Dict[str, Any]:
        """API Authentication service"""
        async with self.session as session:
            query = select(User).where(User.email == data.email)
            result = await session.execute(query)
            user = result.scalars().first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid Credentials",
                )
            
            is_valid_password = checkpw(
                password=data.password.encode("utf-8"),
                hashed_password=user.password,
            )
            if not is_valid_password:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid Credentials",
                )
            
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