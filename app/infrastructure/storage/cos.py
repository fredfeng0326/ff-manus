#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026-05-08 10:53
@Author  : fred.feng0326@gmail.com
@File    : cos.py
"""
import logging
from functools import lru_cache
from typing import Optional

from qcloud_cos import CosS3Client, CosConfig

from core.config import Settings, get_settings

logger = logging.getLogger(__name__)


class Cos:
    """Tencent Cloud COS object storage."""

    def __init__(self):
        """Constructor that loads configuration and initializes COS client attributes."""
        self._settings: Settings = get_settings()
        self._client: Optional[CosS3Client] = None

    async def init(self) -> None:
        """Create the Tencent Cloud COS client."""
        # 1. Check whether the client already exists; if it does, log and stop
        if self._client is not None:
            logger.warning("Tencent Cloud COS is already initialized; skipping re-initialization.")
            return

        try:
            # 2. Create COS configuration
            config = CosConfig(
                Region=self._settings.cos_region,
                SecretId=self._settings.cos_secret_id,
                SecretKey=self._settings.cos_secret_key,
                Token=None,
                Scheme=self._settings.cos_scheme,
            )
            self._client = CosS3Client(config)
            logger.info("Tencent Cloud COS initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize Tencent Cloud COS: {str(e)}")
            raise

    async def shutdown(self) -> None:
        """Shut down Tencent Cloud COS object storage."""
        if self._client is not None:
            self._client = None
            logger.info("Tencent Cloud COS shut down successfully.")

        get_cos.cache_clear()

    @property
    def client(self) -> CosS3Client:
        """Read-only property returning the Tencent Cloud COS client."""
        if self._client is None:
            raise RuntimeError("Tencent Cloud COS is not initialized. Please call init() first.")
        return self._client


@lru_cache()
def get_cos() -> Cos:
    """Get the Tencent Cloud COS object storage instance."""
    return Cos()
