#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026-05-10 14:09
@Author  : fred.feng0326@gmail.com
@File    : service_dependencies.py
"""
import logging
from functools import lru_cache

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.app_config_service import AppConfigService
from app.application.services.status_service import StatusService
from app.infrastructure.external.health_checker.postgres_health_checker import PostgresHealthChecker
from app.infrastructure.external.health_checker.redis_health_checker import RedisHealthChecker
from app.infrastructure.repostories.file_app_config_repository import FileAppConfigRepository
from app.infrastructure.storage.postgres import get_db_session
from app.infrastructure.storage.redis import get_redis, RedisClient
from core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


@lru_cache()
def get_app_config_service() -> AppConfigService:
    # 1. Build the repository and log
    logger.info("Loading AppConfigService")
    file_app_config_repository = FileAppConfigRepository(settings.app_config_filepath)

    # 2. Instantiate APPConfigService
    return AppConfigService(app_config_repository=file_app_config_repository)


def get_status_service(
        db_session: AsyncSession = Depends(get_db_session),
        redis_client: RedisClient = Depends(get_redis),
) -> StatusService:
    """get_status_service"""
    # 1.initialize postgres and redis health check
    postgres_checker = PostgresHealthChecker(db_session)
    redis_checker = RedisHealthChecker(redis_client)

    # 2.create service and return
    logger.info("loading postgres and redis StatusService")
    return StatusService(checkers=[postgres_checker, redis_checker])
