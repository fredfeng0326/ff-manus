#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026-05-08 10:15
@Author  : fred.feng0326@gmail.com
@File    : postgres.py
"""
import logging
from functools import lru_cache
from typing import Optional

# from app.infrastructure.repositories.db_uow import DBUnitOfWork
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from core.config import get_settings

logger = logging.getLogger(__name__)


class Postgres:
    """Base Postgres class for database connection and related configuration operations."""

    def __init__(self):
        """Constructor that creates the Postgres engine and session factory."""
        self._engine: Optional[AsyncEngine] = None
        self._session_factory: Optional[async_sessionmaker] = None
        self._settings = get_settings()

    async def init(self) -> None:
        """Initialize the Postgres connection."""
        # 1. Check whether the engine has already been created; if connected, skip repeated initialization
        if self._engine is not None:
            logger.warning("Postgres engine is already initialized; skipping re-initialization.")
            return

        try:
            # 2. Create the async engine
            logger.info("Initializing Postgres connection...")
            self._engine = create_async_engine(
                self._settings.sqlalchemy_database_uri,
                echo=True if self._settings.env == "development" else False,
                pool_pre_ping=True,
                # Check connection validity before borrowing from pool to avoid using closed connections
            )

            # 3. Create the session factory
            self._session_factory = async_sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self._engine,
            )
            logger.info("Postgres session factory created successfully.")

            # 4. Connect to Postgres and perform pre-operations
            async with self._engine.begin() as async_conn:
                # 5. Ensure the UUID extension is installed; install it if missing
                await async_conn.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";'))
                logger.info("Connected to Postgres and ensured uuid-ossp extension is installed.")
        except Exception as e:
            logger.error(f"Failed to connect to Postgres: {str(e)}")
            raise

    async def shutdown(self) -> None:
        """Close the Postgres connection."""
        if self._engine:
            await self._engine.dispose()
            self._engine = None
            self._session_factory = None
            logger.info("Postgres connection closed successfully.")

        # 2. Clear cache
        get_postgres.cache_clear()

    @property
    def session_factory(self) -> async_sessionmaker[AsyncSession]:
        """Read-only property that returns the initialized session factory."""
        if self._session_factory is None:
            raise RuntimeError("Postgres is not initialized. Please call init() first.")
        return self._session_factory


@lru_cache()
def get_postgres() -> Postgres:
    """Get the Postgres instance."""
    return Postgres()


async def get_db_session() -> AsyncSession:
    """FastAPI dependency that asynchronously provides a DB session per request and ensures proper cleanup."""
    # 1. Get the engine and session factory
    db = get_postgres()
    session_factory = db.session_factory

    # 2. Create a session context and complete data operations within it
    async with session_factory() as session:
        try:
            yield session
        except Exception as _:
            await session.rollback()
            raise


def get_session_factory():
    """Get the database session factory."""
    db = get_postgres()
    return db.session_factory

# def get_uow() -> IUnitOfWork:
#     return DBUnitOfWork(session_factory=get_session_factory())
