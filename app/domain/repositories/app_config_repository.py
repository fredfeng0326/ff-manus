#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026-05-10 14:02
@Author  : fred.feng0326@gmail.com
@File    : app_config_repository.py
"""
from typing import Protocol, Optional

from app.domain.models.app_config import AppConfig


class AppConfigRepository(Protocol):
    """Repository for application configuration."""

    def load(self) -> Optional[AppConfig]:
        """Load and return application configuration."""
        ...

    def save(self, app_config: AppConfig) -> None:
        """Persist updated application configuration."""
        ...
