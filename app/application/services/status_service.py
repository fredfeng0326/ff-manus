#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026-05-11 12:51
@Author  : fred.feng0326@gmail.com
@File    : status_service.py
"""
import asyncio
from typing import List

from app.domain.external.health_checker import HealthChecker
from app.domain.models.health_status import HealthStatus


class StatusService:
    """Status service: runs health checks across registered dependencies."""

    def __init__(self, checkers: List[HealthChecker]) -> None:
        """Initialize with all health checkers to run."""
        self._checkers = checkers

    async def check_all(self) -> List[HealthStatus]:
        """Run every checker concurrently and return a list of health statuses."""
        # 1. Run all checks in parallel
        results = await asyncio.gather(
            *(checker.check() for checker in self._checkers),
            return_exceptions=True,  # Surface per-checker failures without failing the whole gather
        )

        # 2. Normalize exceptions into HealthStatus entries
        processed_results = []
        for res in results:
            if isinstance(res, Exception):
                # 3. Checker raised: record as error status
                processed_results.append(HealthStatus(
                    service="unknown",
                    status="error",
                    details=f"Health checker raised an error: {str(res)}"
                ))
            else:
                processed_results.append(res)

        return processed_results
