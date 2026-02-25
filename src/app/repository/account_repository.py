from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.models.schemas import User
from app.schemas.auth_schemas import SignupSchema

class AccountRepository:

    """Repository class to handle database operations related to user accounts."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_account(self, data: SignupSchema, hashed_password: bytes) -> User:

        new_user = User(
            name=data.name,
            email=data.email,
            password=hashed_password,
            admin=data.admin
        )

        self.session.add(new_user)
        await self.session.flush()

        return new_user
    
    async def get_account_by_email(self, email: str):
        query = select(User).where(User.email == email)
        result = await self.session.execute(query)
        return result.scalars().first()
    
    async def get_account_by_id(self, user_id: int):
        user = await self.session.get(User, user_id)
        return user