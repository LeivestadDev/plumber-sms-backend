import os

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

_raw_url = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./svardirekte.db")

connect_args: dict = {}

if "postgresql" in _raw_url or _raw_url.startswith("postgres://"):
    # Normalize scheme to postgresql+asyncpg://
    if _raw_url.startswith("postgres://"):
        _raw_url = _raw_url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif _raw_url.startswith("postgresql://"):
        _raw_url = _raw_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    elif _raw_url.startswith("postgresql+psycopg://"):
        _raw_url = _raw_url.replace("postgresql+psycopg://", "postgresql+asyncpg://", 1)

    # asyncpg does not support sslmode/channel_binding URL params — strip them
    # and pass ssl via connect_args instead
    needs_ssl = "sslmode=require" in _raw_url or "ssl=require" in _raw_url
    _raw_url = _raw_url.split("?")[0]  # strip all query params
    if needs_ssl:
        connect_args = {"ssl": True}

DATABASE_URL = _raw_url

engine = create_async_engine(DATABASE_URL, echo=False, connect_args=connect_args)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


async def init_db() -> None:
    from app import models  # noqa: F401 — registers models with Base.metadata

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
