import os
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from jose import jwt, JWTError
from dotenv import load_dotenv

from ..db.connection import get_database
from ..db.models.schemas import User

from main import oauth2_schema

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
    session: AsyncSession = Depends(get_database)
) -> str:
    try:
        user_id = await validate_access_token(token_jwt=token)
        query = select(User).where(User.id == int(user_id))
        result = await session.execute(query)
        get_user = result.scalars().first()
        if not get_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Access denied"
            )
        request.state.user_id = user_id
        return user_id
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid or expired access token."
        )