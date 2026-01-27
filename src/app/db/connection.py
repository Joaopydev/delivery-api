import os
from dotenv import load_dotenv
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncSession
from sqlalchemy.orm import sessionmaker

load_dotenv()

APP_DATA_BASE = os.getenv("DATA_BASE_URL")
DATA_BASE_URL = os.environ.get("DATA_BASE_URL_WORKER", APP_DATA_BASE)

# Engine assíncrona
engine: None | AsyncEngine = None

def get_engine() -> AsyncEngine:
    global engine
    
    if engine is None:
        engine = create_async_engine(
            url=DATA_BASE_URL,
            echo=True,
            future=True
        )
    return engine

# Fábrica de sessões assíncronas
async_session = sessionmaker(
    bind=get_engine(),
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

async def get_database():
    try:
        session = async_session()
        yield session
    finally:
        await session.close()

@asynccontextmanager
async def get_session_to_worker():
    try:
        session = async_session()
        yield session
    finally:
        await session.close()