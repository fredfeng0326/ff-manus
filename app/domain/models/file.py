#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026-05-08 10:18
@Author  : fred.feng0326@gmail.com
@File    : file.py
"""
import uuid

from pydantic import BaseModel, Field


class File(BaseModel):
    """Domain model for a file uploaded or produced by Manus or a human."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))  # File id
    filename: str = ""  # Original filename
    filepath: str = ""  # Local or logical file path
    key: str = ""  # Object key in Tencent Cloud COS
    extension: str = ""  # File extension
    mime_type: str = ""  # MIME type
    size: int = 0  # Size in bytes
