#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026-05-08 10:19
@Author  : fred.feng0326@gmail.com
@File    : memory.py
"""
import logging
from typing import List, Dict, Any, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class Memory(BaseModel):
    """Memory model that stores core message history for an agent."""
    messages: List[Dict[str, Any]] = Field(default_factory=list)

    @classmethod
    def get_message_role(cls, message: Dict[str, Any]) -> str:
        """Get the role field from a message."""
        return message.get("role")

    def add_message(self, message: Dict[str, Any]) -> None:
        """Add a single message to memory."""
        self.messages.append(message)

    def add_messages(self, messages: List[Dict[str, Any]]) -> None:
        """Add multiple messages to memory."""
        self.messages.extend(messages)

    def get_messages(self) -> List[Dict[str, Any]]:
        """Return all messages in memory."""
        return self.messages

    def get_last_message(self) -> Optional[Dict[str, Any]]:
        """Return the last message in memory, or None if empty."""
        return self.messages[-1] if len(self.messages) > 0 else None

    def roll_back(self) -> None:
        """Roll back memory by removing the last message."""
        self.messages = self.messages[:-1]

    def compact(self) -> None:
        """Compact memory by trimming heavy tool outputs and reasoning context."""
        # 1. Iterate through all messages
        for message in self.messages:
            # 2. Check whether the message role is tool
            if self.get_message_role(message) == "tool":
                if message.get("function_name") in ["browser_view", "browser_navigate"]:
                    message["content"] = "(removed)"
                    logger.debug(f"Removed tool result from memory: {message['function_name']}")

            # 3. Remove reasoning_content to reduce context size during compaction
            if "reasoning_content" in message:
                logger.debug(f"Removed reasoning content from memory: {message['reasoning_content'][:50]}...")
                del message["reasoning_content"]

    @property
    def empty(self) -> bool:
        """Read-only property indicating whether memory is empty."""
        return len(self.messages) == 0
