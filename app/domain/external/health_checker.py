#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026-05-11 12:52
@Author  : fred.feng0326@gmail.com
@File    : health_checker.py
"""
from typing import Protocol

from app.domain.models.health_status import HealthStatus


class HealthChecker(Protocol):
    """service health checker Protocol"""

    async def check(self) -> HealthStatus:
        """for checking app health"""
        ...
