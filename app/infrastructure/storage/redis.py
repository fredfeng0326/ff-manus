#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026-05-08 10:01
@Author  : fred.feng0326@gmail.com
@File    : redis.py
"""

import logging
from functools import lru_cache

from redis.asyncio import Redis

from core.config import get_settings, Settings

logger = logging.getLogger(__name__)


class RedisClient:
    """Redis client used to connect to and work with the Redis cache."""

    def __init__(self):
        """Constructor that creates the Redis client."""
        self._client: Redis | None = None
        self._settings: Settings = get_settings()

    async def init(self) -> None:
        """Initialize the Redis client."""
        # 1. Check whether the client already exists; if so, it is already connected and no further action is needed
        if self._client:
            logger.warning("Redis client is already initialized; skipping re-initialization.")
            return

        try:
            # 2. Create the Redis client and connect
            self._client = Redis(
                host=self._settings.redis_host,
                port=self._settings.redis_port,
                db=self._settings.redis_db,
                password=self._settings.redis_password,
                decode_responses=True,
            )

            # 3. Test the connection to the Redis cache
            await self._client.ping()
            logger.info("Redis client initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize Redis client: {str(e)}")
            raise

    async def shutdown(self) -> None:
        """Operations to perform when shutting down Redis."""
        # 1. If the client exists, close it and log a message
        if self._client is not None:
            await self._client.aclose()
            self._client = None
            logger.info("Redis client closed successfully.")

        # 2. Clear the cache
        get_redis.cache_clear()

    @property
    def client(self) -> Redis:
        """Read-only property that returns the Redis client instance."""
        if self._client is None:
            raise RuntimeError("Redis client is not initialized; failed to get client.")
        return self._client


@lru_cache()
def get_redis() -> RedisClient:
    """Get the Redis client instance."""
    return RedisClient()
