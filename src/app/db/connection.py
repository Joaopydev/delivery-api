import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv

from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncSession
from sqlalchemy.orm import sessionmaker

load_dotenv()

APP_DATA_BASE = os.getenv("DATA_BASE_URL")
DATA_BASE_URL = os.environ.get("DATA_BASE_URL_WORKER", APP_DATA_BASE)

def get_engine() -> AsyncEngine:
    return create_async_engine(
        url=DATA_BASE_URL,
        echo=True,
        future=True
    )

# Fábrica de sessões assíncronas
async_session = sessionmaker(
    bind=get_engine(),
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

async def get_database():
    session = async_session()
    try:
        yield session
        await session.commit()
    except:
        await session.rollback()
        raise
    finally:
        await session.close()

@asynccontextmanager
async def get_session_to_worker():
    session = async_session()
    try:
        yield session
        await session.commit()
    except:
        await session.rollback()
        raise
    finally:
        await session.close()
