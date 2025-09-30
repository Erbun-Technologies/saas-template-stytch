import os
from typing import Optional

import asyncio
import time
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@db:5432/saas",
)

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    pool_pre_ping=True,
)
async_session: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()


async def init_db(timeout_seconds: int = 60) -> None:
    """Create tables if they don't exist (template: no migrations).

    Retries for a limited time to allow the DB container to become ready.
    """
    # Import models to register metadata before create_all
    from . import models  # noqa: F401

    deadline = time.monotonic() + timeout_seconds
    last_err: Optional[Exception] = None
    while time.monotonic() < deadline:
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            return
        except Exception as exc:  # pragma: no cover - startup race handling
            last_err = exc
            await asyncio.sleep(1.5)
    if last_err:
        raise last_err
