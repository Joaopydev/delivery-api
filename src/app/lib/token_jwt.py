import os
from datetime import datetime, timedelta, timezone

from fastapi import Depends, Request

from jose import jwt, JWTError
from dotenv import load_dotenv

from app.dependencies.account_dependencies import get_account_repository
from app.repository.account_repository import AccountRepository

from app.core.security import oauth2_schema
from app.core.exceptions import (
    InvalidAccessTokenError,
    AccessDeniedError,
    RequireAdminError,
)

load_dotenv()

async def load_pem_key(key_env_var: str) -> bytes:
    """
    Carrega a chave PEM de uma variável de ambiente e a formata
    corretamente para PyJWT, garantindo que seja um objeto bytes.
    """
    key_str = os.getenv(key_env_var)
    if not key_str:
        raise ValueError(f"Environment variable {key_env_var} not found.")

    # Esta linha é crucial para restaurar as quebras de linha em chaves PEM
    key_str = key_str.strip().replace('\\n', '\n').replace('"', '')

    return key_str.encode('utf-8')

async def signin_access_token(
    user_id: str,
    token_duration=timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))),
):
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "iss": os.getenv("ISSUER"),
        "iat": int(now.timestamp()),
        "exp": now + token_duration
    }

    private_key = await load_pem_key("SECRET_JWT_PRIVATE_KEY")

    access_token = jwt.encode(
        claims=payload,
        key=private_key,
        algorithm="RS256",
    )
    return access_token


async def validate_access_token(token_jwt: str):
    public_key = await load_pem_key("SECRET_JWT_PUBLIC_KEY")
    payload_data = jwt.decode(
        token=token_jwt,
        key=public_key,
        algorithms=["RS256"],
        options={
            "verify_signature": True,
            "verify_aud": False, # Não estamos usando 'aud' (audience)
            "verify_iss": True,  # Queremos verificar o 'iss'
            "require_iss": True, # O 'iss' é obrigatório
        },
    )
    return payload_data["sub"]

async def verify_token(
    request: Request,
    token: str = Depends(oauth2_schema),
    account_repository: AccountRepository = Depends(get_account_repository),
) -> str:
    try:
        user_id = await validate_access_token(token_jwt=token)
        get_user = await account_repository.get_account_by_id(int(user_id))
        if not get_user:
            raise AccessDeniedError()

        request.state.user = get_user.to_dict_necessary_attributes
        return user_id
    except JWTError as exc:
        raise InvalidAccessTokenError() from exc

async def require_admin(
    user_id: str = Depends(verify_token),
    account_repository: AccountRepository = Depends(get_account_repository),
) -> None:

    user = await account_repository.get_account_by_id(int(user_id))
    if not user.admin:
        raise RequireAdminError()
