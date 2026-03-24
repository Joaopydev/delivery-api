from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.connection import get_database
from app.repository.account_repository import AccountRepository
from app.services.account.signin import SigninService
from app.services.account.signup import SignupService


def get_account_repository(session: AsyncSession = Depends(get_database)) -> AccountRepository:
    return AccountRepository(session=session)

def get_signin_service(account_repository: AccountRepository = Depends(get_account_repository)) -> SigninService:
    return SigninService(account_repository=account_repository)

def get_signup_service(account_repository: AccountRepository = Depends(get_account_repository)) -> SignupService:
    return SignupService(account_repository=account_repository)
