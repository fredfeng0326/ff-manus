#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026-05-06 14:27
@Author  : fred.feng0326@gmail.com
@File    : logging.py
"""
import logging
import sys

from core.config import get_settings


def setup_logging():
    """Configure the logging system for the MoocManus project, including level, format, and output destinations."""
    # 1. Retrieve project settings
    settings = get_settings()

    # 2. Get the root logger
    root_logger = logging.getLogger()

    # 3. Clear existing handlers to avoid conflicts or duplicates with uvicorn's dictConfig reconfiguration
    root_logger.handlers.clear()

    # 4. Set the log level for the root logger
    log_level = getattr(logging, settings.log_level)
    root_logger.setLevel(log_level)

    # 5. Define the log output format
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 6. Create a console log handler (use stderr, which is unbuffered in Python and more reliable in Docker)
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)

    # 7. Attach the console handler to the root logger
    root_logger.addHandler(console_handler)

    root_logger.info("Logging system initialized successfully")
