import os
from typing import Dict, Any, Optional
from datetime import timedelta
from dotenv import load_dotenv

from bcrypt import hashpw, gensalt
from fastapi import HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ...db.models.schemas import User
from ...schemas.auth_schemas import SignupSchema

from ...lib.token_jwt import signin_access_token

load_dotenv()


class SignupService:

    def __init__(self, session: Optional[AsyncSession]):
        self.session = session

    async def account_creation_service(self, data: SignupSchema) -> Dict[str, Any]:
        async with self.session as session:
            query = select(User).where(User.email == data.email)
            result = await session.execute(query)
            user = result.scalars().first()
            if user:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email already exists"
                )
            
            hashed_password = hashpw(
                password=data.password.encode("utf-8"),
                salt=gensalt(8)
            )

            new_user = User(
                name=data.name,
                email=data.email,
                password=hashed_password
            )

            session.add(new_user)
            await session.commit()
            await session.refresh(new_user)

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
