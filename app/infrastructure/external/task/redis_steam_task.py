#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026-05-11 14:47
@Author  : fred.feng0326@gmail.com
@File    : redis_steam_task.py
"""
import asyncio
import logging
import uuid
from typing import Optional, Dict

from app.domain.external.message_queue import MessageQueue
from app.domain.external.task import Task, TaskRunner
from app.infrastructure.external.message_queue.redis_stream_message_queue import RedisStreamMessageQueue

logger = logging.getLogger(__name__)


class RedisStreamTask(Task):
    """Task implementation backed by Redis Streams for input/output queues."""

    # In-memory registry of all active tasks (by task id)
    _task_registry: Dict[str, "RedisStreamTask"] = {}

    def __init__(self, task_runner: TaskRunner) -> None:
        """Initialize task with the given runner and stream-backed I/O."""
        self._task_runner = task_runner
        self._id = str(uuid.uuid4())
        self._execution_task: Optional[asyncio.Task] = None  # Background asyncio task for execution

        input_stream_name = f"task:input:{self._id}"
        output_stream_name = f"task:output:{self._id}"

        self._input_stream = RedisStreamMessageQueue(input_stream_name)
        self._output_stream = RedisStreamMessageQueue(output_stream_name)

        # Register this instance in the global registry
        RedisStreamTask._task_registry[self._id] = self

    def _cleanup_registry(self) -> None:
        """Remove this task from the global registry."""
        if self._id in RedisStreamTask._task_registry:
            del RedisStreamTask._task_registry[self._id]
            logger.info(f"Task [{self._id}] removed from registry")

    def _on_task_done(self) -> None:
        """Called when execution finishes (success, error, or cancel)."""
        # 1. Notify task runner if present
        if self._task_runner:
            asyncio.create_task(self._task_runner.on_done(self))

        # 2. Drop registry entry for this task
        self._cleanup_registry()

    async def _execute_task(self) -> None:
        """Run the task via TaskRunner.invoke."""
        try:
            await self._task_runner.invoke(self)
        except asyncio.CancelledError:
            logger.info(f"Task [{self._id}] execution was cancelled")
            raise
        except Exception as e:
            logger.error(f"Task [{self._id}] raised an error: {str(e)}")
        finally:
            self._on_task_done()

    async def invoke(self) -> None:
        """Start execution using the configured task runner."""
        if self.done:
            self._execution_task = asyncio.create_task(self._execute_task())
            logger.info(f"Task [{self._id}] started")

    def cancel(self) -> bool:
        """Cancel the running asyncio task if still active."""
        if not self.done:
            # 1. Cancel the background task
            self._execution_task.cancel()
            logger.info(f"Task [{self._id}] cancelled")

            # 2. Remove from registry
            self._cleanup_registry()
            return True

        # 3. Already finished; still ensure registry is clean
        self._cleanup_registry()
        return True

    @property
    def input_stream(self) -> MessageQueue:
        return self._input_stream

    @property
    def output_stream(self) -> MessageQueue:
        return self._output_stream

    @property
    def id(self) -> str:
        return self._id

    @property
    def done(self) -> bool:
        if self._execution_task is None:
            return True
        return self._execution_task.done()

    @classmethod
    def get(cls, task_id: str) -> Optional["Task"]:
        return RedisStreamTask._task_registry.get(task_id)

    @classmethod
    def create(cls, task_runner: TaskRunner) -> "Task":
        return cls(task_runner)

    @classmethod
    async def destroy(cls) -> None:
        for task_id in RedisStreamTask._task_registry:
            # 1. Resolve task by id
            task = RedisStreamTask._task_registry[task_id]
            task.cancel()

            # 2. Tear down task runner if present
            if task._task_runner:
                await task._task_runner.destroy()

        # 3. Clear the global registry
        cls._task_registry.clear()
