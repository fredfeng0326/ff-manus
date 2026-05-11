#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026-05-11 13:52
@Author  : fred.feng0326@gmail.com
@File    : task.py
"""
from abc import ABC, abstractmethod
from typing import Protocol, Optional

from app.domain.external.message_queue import MessageQueue


class TaskRunner(ABC):
    """Runs tasks: how to execute them and tear them down to free resources."""

    @abstractmethod
    async def invoke(self, task: "Task") -> None:
        """Run the given task."""
        raise NotImplementedError

    @abstractmethod
    async def destroy(self) -> None:
        """Tear down tasks and release resources (e.g. close connections, free memory, clean temp data, stop background work)."""
        raise NotImplementedError

    @abstractmethod
    async def on_done(self, task: "Task") -> None:
        """Callback invoked when a task finishes."""
        raise NotImplementedError


class Task(Protocol):
    """Protocol for task lifecycle and I/O streams."""

    async def invoke(self) -> None:
        """Run this task."""
        ...

    def cancel(self) -> bool:
        """Cancel this task."""
        ...

    @property
    def input_stream(self) -> MessageQueue:
        """Read-only: task input message queue."""
        ...

    @property
    def output_stream(self) -> MessageQueue:
        """Read-only: task output message queue."""
        ...

    @property
    def id(self) -> str:
        """Read-only: task identifier."""
        ...

    @property
    def done(self) -> bool:
        """Read-only: whether the task has finished."""
        ...

    @classmethod
    def get(cls, task_id: str) -> Optional["Task"]:
        """Return the task for the given id, if any."""
        ...

    @classmethod
    def create(cls, task_runner: TaskRunner) -> "Task":
        """Create a task bound to the given task runner."""
        ...

    @classmethod
    async def destroy(cls) -> None:
        """Destroy all task instances."""
        ...
