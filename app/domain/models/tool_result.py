#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026-05-11 18:20
@Author  : fred.feng0326@gmail.com
@File    : tool_result.py
"""
from typing import Optional, TypeVar, Generic

from pydantic import BaseModel

T = TypeVar("T")


class ToolResult(BaseModel, Generic[T]):
    """Domain model for a tool invocation result."""
    success: bool = True  # Whether the call succeeded
    message: Optional[str] = ""  # Optional human-readable message
    data: Optional[T] = None  # Tool output payload

    @classmethod
    def from_sandbox(cls, code: int, msg: str, data: Optional[T], **kwargs) -> "ToolResult":
        """Build a ToolResult from sandbox API response fields."""
        return cls(
            success=True if code < 300 else False,
            message=msg,
            data=data,
        )
