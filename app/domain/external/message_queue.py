#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026-05-11 13:53
@Author  : fred.feng0326@gmail.com
@File    : message_queue.py
"""
from typing import Protocol, Any, Tuple


class MessageQueue(Protocol):
    """Protocol for an async message queue."""

    async def put(self, message: Any) -> str:
        """Enqueue a message; returns the assigned message id."""
        ...

    async def get(self, start_id: str = None, block_ms: int = None) -> Tuple[str, Any]:
        """Fetch one message after start_id, optionally blocking up to block_ms milliseconds."""
        ...

    async def pop(self) -> Tuple[str, Any]:
        """Remove and return the first message in the queue."""
        ...

    async def clear(self) -> None:
        """Remove all messages from the queue."""
        ...

    async def is_empty(self) -> bool:
        """Return True if the queue has no messages."""
        ...

    async def size(self) -> int:
        """Return the number of messages in the queue."""
        ...

    async def delete_message(self, message_id: str) -> bool:
        """Delete the message with the given id; return True if it existed and was removed."""
        ...
