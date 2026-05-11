#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026-05-10 14:11
@Author  : fred.feng0326@gmail.com
@File    : file_app_config_repository.py
"""
import logging
from pathlib import Path
from typing import Optional

import yaml
from filelock import FileLock

from app.application.errors.exceptions import ServerRequestsError
from app.domain.models.app_config import AppConfig, LLMConfig, AgentConfig, MCPConfig, A2AConfig
from app.domain.repositories.app_config_repository import AppConfigRepository

logger = logging.getLogger(__name__)


class FileAppConfigRepository(AppConfigRepository):
    """Application configuration repository backed by a local file."""

    def __init__(self, config_path: str) -> None:
        """Constructor that initializes the file-backed configuration repository."""
        # 1. Use the current working directory as the project root
        root_dir = Path.cwd()

        # 2. Resolve the config file path and ensure parent directories exist
        self._config_path = root_dir.joinpath(root_dir, config_path)
        self._config_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock_file = self._config_path.with_suffix(".lock")  # Lock file for concurrent writes

    def _create_default_app_config_if_not_exists(self):
        """If the config file is missing, create default settings and write them to disk."""
        if not self._config_path.exists():
            default_app_config = AppConfig(
                llm_config=LLMConfig(),
                agent_config=AgentConfig(),
                mcp_config=MCPConfig(),
                a2a_config=A2AConfig(),
            )
            self.save(default_app_config)

    def load(self) -> Optional[AppConfig]:
        """Load application configuration from the local YAML file."""
        # 1. Ensure a default config file exists
        self._create_default_app_config_if_not_exists()

        try:
            # 2. Read the file and parse into AppConfig
            with open(self._config_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                return AppConfig.model_validate(data) if data else None
        except Exception as e:
            logger.error(f"读取应用配置失败: {str(e)}")
            raise ServerRequestsError("读取应用配置失败，请稍后尝试")

    def save(self, app_config: AppConfig) -> None:
        """Persist app_config to the local YAML file."""
        # 1. Acquire a lock before writing
        lock = FileLock(self._lock_file, timeout=5)

        try:
            with lock:
                # 2. Serialize app_config to a JSON-compatible dict
                data_to_dump = app_config.model_dump(mode="json")

                # 3. Write the YAML file
                with open(self._config_path, "w", encoding="utf-8") as f:
                    yaml.dump(data_to_dump, f, allow_unicode=True, sort_keys=False)
        except TimeoutError:
            logger.error("无法获取配置文件")
            raise ServerRequestsError("写入配置文件失败，请稍后尝试")
