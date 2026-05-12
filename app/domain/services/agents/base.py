#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026-05-12 11:33
@Author  : fred.feng0326@gmail.com
@File    : base.py
"""
import asyncio
import logging
import uuid
from abc import ABC
from typing import Optional, List, AsyncGenerator, Dict, Any, Callable

from app.domain.external.json_parser import JSONParser
from app.domain.external.llm import LLM
from app.domain.models.app_config import AgentConfig
from app.domain.models.event import ToolEvent, ToolEventStatus, ErrorEvent, MessageEvent, BaseEvent
from app.domain.models.memory import Memory
from app.domain.models.message import Message
from app.domain.models.tool_result import ToolResult
from app.domain.repositories.uow import IUnitOfWork
from app.domain.services.tools.base import BaseTool

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Abstract base class for an LLM-backed agent."""
    name: str = ""  # Agent display / registry name
    _system_prompt: str = ""  # System prompt injected into memory
    _format: Optional[str] = None  # Optional structured response format for the LLM
    _retry_interval: float = 1.0  # Delay between retries (seconds)
    _tool_choice: Optional[str] = None  # Optional tool_choice override for the LLM

    def __init__(
            self,
            uow_factory: Callable[[], IUnitOfWork],
            session_id: str,  # Conversation session id
            agent_config: AgentConfig,  # Agent runtime limits (retries, iterations, etc.)
            llm: LLM,  # LLM protocol implementation
            json_parser: JSONParser,  # Parser for tool-call JSON from the model
            tools: List[BaseTool],  # Registered tool groups
    ) -> None:
        """Wire dependencies and open a unit-of-work scope for this agent."""
        self._uow_factory = uow_factory
        self._uow = uow_factory()
        self._session_id = session_id
        self._agent_config = agent_config
        self._llm = llm
        self._memory: Optional[Memory] = None
        self._json_parser = json_parser
        self._tools = tools

    async def _ensure_memory(self) -> None:
        """Load session memory from persistence if not already cached."""
        if self._memory is None:
            async with self._uow:
                self._memory = await self._uow.session.get_memory(self._session_id, self.name)

    def _get_available_tools(self) -> List[Dict[str, Any]]:
        """Flatten OpenAI-style tool schemas from all tool groups."""
        available_tools = []
        for tool in self._tools:
            available_tools.extend(tool.get_tools())
        return available_tools

    def _get_tool(self, tool_name: str) -> BaseTool:
        """Return the tool group that exposes the given function name."""
        # 1. Scan each tool group
        for tool in self._tools:
            # 2. Match by registered tool name
            if tool.has_tool(tool_name):
                return tool

        raise ValueError(f"Unknown tool: {tool_name}")

    async def _invoke_llm(self, messages: List[Dict[str, Any]], format: Optional[str] = None) -> Dict[str, Any]:
        """Append messages, call the LLM with retries, and persist assistant output to memory."""
        # 1. Persist incoming messages
        await self._add_to_memory(messages)

        # 2. Build optional response_format payload
        response_format = {"type": format} if format else None

        # 3. Retry loop up to max_retries
        error = "LLM invocation failed"
        for _ in range(self._agent_config.max_retries):
            try:
                # 4. Call the model
                message = await self._llm.invoke(
                    messages=self._memory.get_messages(),
                    tools=self._get_available_tools(),
                    response_format=response_format,
                    tool_choice=self._tool_choice,
                )

                # 5. Handle empty assistant replies
                if message.get("role") == "assistant":
                    if not message.get("content") and not message.get("tool_calls"):
                        logger.warning("LLM returned an empty assistant message; retrying")
                        await self._add_to_memory([
                            {"role": "assistant", "content": ""},
                            {
                                "role": "user",
                                "content": "The assistant returned no content. Please continue.",
                            },
                        ])
                        await asyncio.sleep(self._retry_interval)
                        continue

                    # 6. Normalize assistant payload (incl. reasoning + single tool call)
                    filtered_message = {"role": "assistant", "content": message.get("content")}
                    if message.get("reasoning_content"):
                        filtered_message["reasoning_content"] = message.get("reasoning_content")
                    if message.get("tool_calls"):
                        # 7. Allow at most one tool call per round
                        filtered_message["tool_calls"] = message.get("tool_calls")[:1]
                else:
                    # 8. Unexpected role: log and pass through
                    logger.warning(f"LLM message has unexpected role: {message.get('role')}")
                    filtered_message = message

                # 9. Persist model output
                await self._add_to_memory([filtered_message])
                return filtered_message
            except Exception as e:
                # 10. Log, wait, retry
                logger.error(f"LLM invocation error: {str(e)}")
                error = str(e)
                await asyncio.sleep(self._retry_interval)
                continue

        # 11. Exhausted retries
        raise RuntimeError(
            f"LLM failed after {self._agent_config.max_retries} retries: {error}"
        )

    async def _invoke_tool(self, tool: BaseTool, tool_name: str, arguments: Dict[str, Any]) -> ToolResult:
        """Invoke a tool with retries; on total failure return a failed ToolResult for the model."""
        # 1. Retry up to max_retries
        err = ""
        for _ in range(self._agent_config.max_retries):
            try:
                return await tool.invoke(tool_name, **arguments)
            except Exception as e:
                err = str(e)
                logger.exception(f"Tool invocation failed [{tool_name}]: {str(e)}")
                await asyncio.sleep(self._retry_interval)
                continue

        # 2. Surface failure as ToolResult for the LLM to handle
        return ToolResult(success=False, message=err)

    async def _add_to_memory(self, messages: List[Dict[str, Any]]) -> None:
        """Append messages and persist memory through the unit of work."""
        # 1. Ensure memory is loaded
        await self._ensure_memory()

        # 2. Seed with system prompt on first write
        if self._memory.empty:
            self._memory.add_message({
                "role": "system", "content": self._system_prompt,
            })

        # 3. Append new messages
        self._memory.add_messages(messages)

        # 4. Persist
        async with self._uow:
            await self._uow.session.save_memory(self._session_id, self.name, self._memory)

    async def compact_memory(self) -> None:
        """Run memory compaction and persist."""
        await self._ensure_memory()
        self._memory.compact()
        async with self._uow:
            await self._uow.session.save_memory(self._session_id, self.name, self._memory)

    async def roll_back(self, message: Message) -> None:
        """Align memory with cancelled or superseded tool rounds (e.g. new user message, pause/stop)."""
        # 1. If last turn was not a tool call, nothing to roll back
        await self._ensure_memory()
        last_message = self._memory.get_last_message()
        if (
                not last_message or
                not last_message.get("tool_calls") or
                len(last_message.get("tool_calls")) == 0
        ):
            return

        # 2. Inspect the pending tool call
        tool_call = last_message.get("tool_calls")[0]

        # 3. Resolve function name and call id
        function_name = tool_call.get("function", {}).get("name")
        tool_call_id = tool_call.get("id")

        # 4. Special-case user notification tool: record outcome instead of popping
        if function_name == "message_ask_user":
            self._memory.add_message({
                "role": "tool",
                "tool_call_id": tool_call_id,
                "function_name": function_name,
                "content": message.model_dump_json(),
            })
        else:
            # 5. Otherwise drop the incomplete assistant/tool turn
            self._memory.roll_back()

        # 6. Persist
        async with self._uow:
            await self._uow.session.save_memory(self._session_id, self.name, self._memory)

    async def invoke(self, query: str, format: Optional[str] = None) -> AsyncGenerator[BaseEvent, None]:
        """Run the agent turn: user query -> LLM loop with optional tools -> final message or error events."""
        # 1. Resolve response format
        format = format if format else self._format

        # 2. First LLM call
        message = await self._invoke_llm(
            [{"role": "user", "content": query}],
            format,
        )

        # 3. Tool loop bounded by max_iterations
        for _ in range(self._agent_config.max_iterations):
            # 4. No tool calls => final natural-language answer
            if not message or not message.get("tool_calls"):
                break

            # 5. Execute each tool call (typically one after filtering)
            tool_messages = []
            for tool_call in message["tool_calls"]:
                if not tool_call.get("function"):
                    continue

                # 6. Parse ids, name, arguments
                tool_call_id = tool_call["id"] or str(uuid.uuid4())
                function_name = tool_call["function"]["name"]
                function_args = await self._json_parser.invoke(tool_call["function"]["arguments"])

                # 7. Resolve tool group
                tool = self._get_tool(function_name)

                # 8. Emit pre-call event (tool_content filled by concrete agents if needed)
                yield ToolEvent(
                    tool_call_id=tool_call_id,
                    tool_name=tool.name,
                    function_name=function_name,
                    function_args=function_args,
                    status=ToolEventStatus.CALLING,
                )

                # 9. Run tool
                result = await self._invoke_tool(tool, function_name, function_args)

                # 10. Emit post-call event
                yield ToolEvent(
                    tool_call_id=tool_call_id,
                    tool_name=tool.name,
                    function_name=function_name,
                    function_args=function_args,
                    function_result=result,
                    status=ToolEventStatus.CALLED,
                )

                # 11. Build tool role messages for the next LLM round
                tool_messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call_id,
                    "function_name": function_name,
                    "content": result.model_dump_json(),
                })

            # 12. Follow-up LLM call with tool outputs
            message = await self._invoke_llm(tool_messages)
        else:
            # 13. for-else: loop finished without break => iteration budget exceeded
            yield ErrorEvent(
                error=(
                    f"Agent exceeded max_iterations ({self._agent_config.max_iterations}); "
                    "task could not be completed."
                )
            )

        # 14. Emit final assistant text or a generic failure
        if message and message.get("content") is not None:
            yield MessageEvent(message=message["content"])
        else:
            yield ErrorEvent(error="Agent did not produce a valid assistant reply.")
