#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026-05-11 12:59
@Author  : fred.feng0326@gmail.com
@File    : postgres_health_checker.py
"""
import logging

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.external.health_checker import HealthChecker
from app.domain.models.health_status import HealthStatus

logger = logging.getLogger(__name__)


class PostgresHealthChecker(HealthChecker):
    """Postgres HealthChecker"""

    def __init__(self, db_session: AsyncSession) -> None:
        self._db_session = db_session

    async def check(self) -> HealthStatus:
        """run simple SQL to check the health of Postgres"""
        try:
            await self._db_session.execute(text("SELECT 1"))
            return HealthStatus(service="postgres", status="ok")
        except Exception as e:
            logger.error(f"Postgres health check error: {str(e)}")
            return HealthStatus(
                service="postgres",
                status="error",
                details=str(e),
            )
