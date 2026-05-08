#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026-05-08 10:17
@Author  : fred.feng0326@gmail.com
@File    : uow.py
"""

from abc import ABC, abstractmethod
from typing import TypeVar

from .file_repository import FileRepository
from .session_repository import SessionRepository

T = TypeVar("T", bound="IUnitOfWork")


class IUnitOfWork(ABC):
    """Protocol interface for the Unit of Work pattern."""
    file: FileRepository
    session: SessionRepository

    @abstractmethod
    async def commit(self):
        """Commit database persistence changes."""
        ...

    @abstractmethod
    async def rollback(self):
        """Roll back database changes."""
        ...

    @abstractmethod
    async def __aenter__(self: T) -> T:
        """Enter the context manager."""
        ...

    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit the context manager."""
        ...
