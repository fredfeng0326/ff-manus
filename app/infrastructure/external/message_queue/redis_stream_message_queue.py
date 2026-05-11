#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026-05-11 14:23
@Author  : fred.feng0326@gmail.com
@File    : redis_stream_message_queue.py
"""
import asyncio
import logging
import uuid
from typing import Any, Tuple, Optional, AsyncGenerator

from app.domain.external.message_queue import MessageQueue
from app.infrastructure.storage.redis import get_redis

logger = logging.getLogger(__name__)


class RedisStreamMessageQueue(MessageQueue):
    """Message queue implementation based on Redis Stream."""

    def __init__(self, stream_name: str) -> None:
        """Initialize Redis Stream queue settings, including stream name and lock expiration."""
        self._stream_name = stream_name
        self._redis = get_redis()
        self._lock_expire_seconds = 10

    async def _acquire_lock(self, lock_key: str, timeout_seconds: int = 5) -> Optional[str]:
        """Acquire a distributed lock using the given lock key."""
        # 1. Create a lock token/value
        lock_value = str(uuid.uuid4())
        end_time = timeout_seconds

        # 2. Retry until timeout
        while end_time > 0:
            # 3. Use Redis SET NX EX to acquire lock with expiration
            result = await self._redis.client.set(
                lock_key,
                lock_value,
                nx=True,  # Set only if key does not exist
                ex=self._lock_expire_seconds,
            )

            # 4. Return lock token if acquired
            if result:
                return lock_value

            # 5. Sleep briefly and reduce remaining timeout
            await asyncio.sleep(0.1)
            end_time -= 0.1

        return None

    async def _release_lock(self, lock_key: str, lock_value: str) -> bool:
        """Release the distributed lock using lock key and token."""
        # 1. Build a Lua script for safe lock release
        release_script = """
        if redis.call("GET", KEYS[1]) == ARGV[1] then
            return redis.call("DEL", KEYS[1])
        else
            return 0
        end
        """

        try:
            # 2. Register script
            script = self._redis.client.register_script(release_script)

            # 3. Execute script with keys + args
            result = await script(keys=[lock_key], args=[lock_value])

            return result == 1
        except Exception:
            return False

    async def put(self, message: Any) -> str:
        """Add one message to Redis Stream and return its id."""
        logger.debug(f"Enqueue message on stream [{self._stream_name}]: {message}")

        return await self._redis.client.xadd(self._stream_name, {"data": message})

    async def get(self, start_id: str = None, block_ms: int = None) -> Tuple[str, Any]:
        """Read one message from Redis Stream."""
        logger.debug(f"Read message from stream [{self._stream_name}], start_id={start_id}")

        # 1. Default start id if not provided
        if start_id is None:
            start_id = '0'

        # 2. Read one entry from the stream
        messages = await self._redis.client.xread(
            {self._stream_name: start_id},
            count=1,
            block=block_ms,
        )

        # 3. Return empty if no result
        if not messages:
            return None, None

        # 4. Extract stream messages
        stream_messages = messages[0][1]
        if not stream_messages:
            return None, None

        # 5. Extract id and payload
        message_id, message_data = stream_messages[0]

        try:
            return message_id, message_data.get("data")
        except Exception as e:
            logger.error(f"Failed to read from stream [{self._stream_name}]: {str(e)}")
            return None, None

    async def pop(self) -> Tuple[str, Any]:
        """Get and remove the first message in the queue."""
        # 1. Log and prepare lock key
        logger.debug(f"Pop first message from stream [{self._stream_name}]")
        lock_key = f"lock:{self._stream_name}:pop"

        # 2. Acquire distributed lock; return empty if failed
        lock_value = await self._acquire_lock(lock_key)
        if not lock_value:
            return None, None

        try:
            # 3. Read first message from stream
            messages = await self._redis.client.xrange(self._stream_name, "-", "+", count=1)
            if not messages:
                return None, None

            # 4. Extract message id and payload
            message_id, message_data = messages[0]

            # 5. Delete message from stream
            await self._redis.client.xdel(self._stream_name, message_id)

            return message_id, message_data.get("data")
        except Exception as e:
            logger.error(f"Error while popping from stream [{self._stream_name}]: {str(e)}")
            return None, None
        finally:
            await self._release_lock(lock_key, lock_value)

    async def clear(self) -> None:
        """Clear all messages in Redis Stream."""
        await self._redis.client.xtrim(self._stream_name, 0)

    async def is_empty(self) -> bool:
        """Check whether Redis Stream is empty."""
        return await self.size() == 0

    async def size(self) -> int:
        """Return Redis Stream length."""
        return await self._redis.client.xlen(self._stream_name)

    async def delete_message(self, message_id: str) -> bool:
        """Delete a message from Redis Stream by message id."""
        try:
            await self._redis.client.xdel(self._stream_name, message_id)
            return True
        except Exception:
            return False

    async def get_range(
            self,
            start_id: str = "-",
            end_id: str = "+",
            count: int = 100,
    ) -> AsyncGenerator[Tuple[str, Any], None]:
        """Yield messages by range (start id, end id, and count) as an async generator."""
        # 1. Fetch messages in range
        messages = await self._redis.client.xrange(self._stream_name, start_id, end_id, count=count)

        # 2. Return if no messages
        if not messages:
            return

        # 3. Iterate through messages and yield id + payload
        for message_id, message_data in messages:
            try:
                yield message_id, message_data.get("data")
            except Exception:
                continue

    async def get_latest_id(self) -> str:
        """Get the latest message id in the queue."""
        # 1. Read the latest item in reverse order with count=1
        messages = await self._redis.client.xrevrange(self._stream_name, "+", "-", count=1)
        if not messages:
            return "0"

        # 2. Return latest message id
        return messages[0][0]
