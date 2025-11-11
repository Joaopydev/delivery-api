import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncSession
from sqlalchemy.orm import sessionmaker
from contextlib import asynccontextmanager
from dotenv import load_dotenv

load_dotenv()

DATA_BASE_URL = os.getenv("DATA_BASE_URL")

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

# Async context manager para o DB
@asynccontextmanager
async def get_database():
    try:
        session = async_session()
        yield session
    finally:
        await session.close()
