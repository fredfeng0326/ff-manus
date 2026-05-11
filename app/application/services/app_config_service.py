#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026-05-10 14:01
@Author  : fred.feng0326@gmail.com
@File    : app_config_service.py
"""
from app.domain.models.app_config import AppConfig, LLMConfig
from app.domain.repositories.app_config_repository import AppConfigRepository


class AppConfigService:
    """Application configuration service."""

    def __init__(self, app_config_repository: AppConfigRepository) -> None:
        """Constructor that initializes the application configuration service."""
        self.app_config_repository = app_config_repository

    async def _load_app_config(self) -> AppConfig:
        """Load application configuration."""
        return self.app_config_repository.load()

    async def get_llm_config(self) -> LLMConfig:
        """Get LLM provider configuration."""
        app_config = await self._load_app_config()
        return app_config.llm_config

    async def update_llm_config(self, llm_config: LLMConfig) -> LLMConfig:
        """Update LLM provider configuration from the given llm_config."""
        # 1. Load application configuration
        app_config = await self._load_app_config()

        # 2. If api_key is empty or whitespace, keep the existing key
        if not llm_config.api_key.strip():
            llm_config.api_key = app_config.llm_config.api_key

        # 3. Update app_config and persist
        app_config.llm_config = llm_config
        self.app_config_repository.save(app_config)

        return app_config.llm_config
